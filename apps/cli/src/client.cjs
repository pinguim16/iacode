"use strict";

// Packaging places the one canonical contract beside this source. There is no network-loaded
// schema, workspace configuration, generated command execution or caller-selected API path.
const http = require("node:http");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const rawProtocol = fs.readFileSync(
  path.join(__dirname, "desktop_protocol.json"),
);
function freeze(value) {
  if (value && typeof value === "object") {
    Object.values(value).forEach(freeze);
    Object.freeze(value);
  }
  return value;
}
const protocol = freeze(JSON.parse(rawProtocol.toString("utf8")));
const protocolDigest = crypto
  .createHash("sha256")
  .update(rawProtocol)
  .digest("hex");
const hash = (value) => crypto.createHash("sha256").update(value).digest("hex");
const mac = (key, material) =>
  crypto.createHmac("sha256", key).update(material).digest("hex");
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const hex = /^[0-9a-f]{64}$/;
const integer = (value, minimum = 0) =>
  Number.isSafeInteger(value) && value >= minimum;
const record = (value) =>
  value !== null && typeof value === "object" && !Array.isArray(value);

class DesktopClientError extends Error {
  constructor(code, message, context = {}) {
    super(message);
    this.name = "DesktopClientError";
    this.code = code;
    this.uncertain = Boolean(context.uncertain);
    this.requestId = context.requestId;
    this.idempotencyKey = context.idempotencyKey;
  }
}

function fail(code, message) {
  throw new DesktopClientError(code, message);
}

function inspectJson(value, visit) {
  const pending = [[value, 0]];
  let nodes = 0;
  while (pending.length) {
    const [item, depth] = pending.pop();
    if (++nodes > protocol.maxJsonNodes || depth > protocol.maxJsonDepth)
      fail(
        "JSON_COMPLEXITY_REFUSED",
        "JSON exceeds the declared depth or node bound",
      );
    if (typeof item === "string") visit(item);
    else if (item && typeof item === "object") {
      for (const [name, child] of Object.entries(item)) {
        visit(name);
        pending.push([child, depth + 1]);
        if (pending.length > protocol.maxJsonNodes)
          fail(
            "JSON_COMPLEXITY_REFUSED",
            "JSON exceeds the declared node bound",
          );
      }
    }
  }
}

function protectData(value, key) {
  const forms =
    typeof key === "string" && hex.test(key)
      ? [key, key.toUpperCase()].flatMap((text) => {
          const bytes = Buffer.from(text);
          return [
            text,
            bytes.toString("base64"),
            bytes.toString("base64url"),
            bytes.toString("hex"),
            [...bytes].map((byte) => `%${byte.toString(16)}`).join(""),
            [...bytes]
              .map((byte) => `\\u${byte.toString(16).padStart(4, "0")}`)
              .join(""),
          ];
        })
      : [];
  inspectJson(value, (text) => {
    if (forms.some((form) => text.includes(form)))
      fail(
        "CREDENTIAL_REFLECTION_REFUSED",
        "protected authentication material is not operation data",
      );
  });
}

function validate(value, schema, location = "arguments") {
  const correct =
    schema.type === "object"
      ? record(value)
      : schema.type === "array"
        ? Array.isArray(value)
        : schema.type === "integer"
          ? Number.isSafeInteger(value)
          : typeof value === schema.type;
  if (!correct) fail("FIELD_TYPE_INVALID", `${location} has the wrong type`);
  if (schema.type === "object") {
    for (const name of schema.required) {
      if (!Object.hasOwn(value, name))
        fail("FIELD_MISSING", `${location}.${name} is required`);
    }
    if (
      Object.keys(value).some((name) => !Object.hasOwn(schema.properties, name))
    ) {
      fail("FIELD_UNKNOWN", `${location} has an undeclared field`);
    }
    for (const [name, item] of Object.entries(value))
      validate(item, schema.properties[name], `${location}.${name}`);
  } else if (schema.type === "array") {
    if (value.length < schema.minItems || value.length > schema.maxItems)
      fail("FIELD_VALUE_INVALID", `${location} has an invalid item count`);
    for (const item of value) validate(item, schema.items, `${location}[]`);
  } else if (schema.type === "string") {
    const chars = Array.from(value);
    const invalidUnicode = chars.some(
      (char) => char.codePointAt(0) >= 0xd800 && char.codePointAt(0) <= 0xdfff,
    );
    const match = schema.pattern
      ? new RegExp(schema.pattern).exec(value)
      : null;
    if (
      invalidUnicode ||
      chars.length < (schema.minLength || 0) ||
      chars.length > schema.maxLength ||
      (schema.pattern && (!match || match[0] !== value))
    )
      fail("FIELD_VALUE_INVALID", `${location} has an invalid value`);
  } else if (value < schema.minimum || value > schema.maximum)
    fail("FIELD_VALUE_INVALID", `${location} is outside its bound`);
}

function endpoint(value) {
  let url;
  try {
    url = new URL(value);
  } catch {
    fail("ENDPOINT_INVALID", "an explicit loopback HTTP endpoint is required");
  }
  if (
    url.protocol !== "http:" ||
    !["127.0.0.1", "[::1]"].includes(url.hostname) ||
    url.username ||
    url.password ||
    url.pathname !== "/" ||
    url.search ||
    url.hash ||
    !url.port ||
    !/^[0-9]+$/.test(url.port)
  )
    fail(
      "ENDPOINT_REFUSED",
      "use http://127.0.0.1:PORT or http://[::1]:PORT without a path",
    );
  // URL canonicalization must not smuggle an integer/hex/short IPv4 spelling or backslash path.
  if (value !== url.origin && value !== `${url.origin}/`)
    fail(
      "ENDPOINT_REFUSED",
      "endpoint must use its exact canonical loopback spelling",
    );
  return url.origin;
}

function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (record(value))
    return Object.fromEntries(
      Object.keys(value)
        .sort()
        .map((name) => [name, canonical(value[name])]),
    );
  return value;
}

function sameSignature(expected, observed) {
  return (
    typeof observed === "string" &&
    hex.test(observed) &&
    crypto.timingSafeEqual(
      Buffer.from(expected, "hex"),
      Buffer.from(observed, "hex"),
    )
  );
}

class DesktopClient {
  #key;
  #session = null;
  #epoch = null;
  #requests = new Set();
  #disposed = false;

  constructor(baseUrl, key) {
    this.baseUrl = endpoint(baseUrl);
    if (typeof key !== "string" || !hex.test(key))
      fail(
        "CREDENTIAL_INVALID",
        "configure a valid desktop credential out of band",
      );
    this.#key = key;
  }

  get connected() {
    return this.#session !== null && !this.#disposed;
  }
  get session() {
    return this.#session ? structuredClone(this.#session) : null;
  }

  assertSafeData(value) {
    protectData(value, this.#key);
  }

  async connect(options = {}) {
    if (this.#disposed) fail("CLIENT_DISPOSED", "client has been disposed");
    this.#session = null;
    this.#epoch = null;
    const { data } = await this.#exchange("hello", {}, options.signal);
    const vocabularies = [
      "operations",
      "runStates",
      "terminalRunStates",
      "qualityStates",
      "terminalQualityStates",
    ];
    if (
      !record(data) ||
      data.authenticated !== true ||
      data.protocolDigest !== protocolDigest ||
      !Number.isFinite(Date.parse(data.expiresAt)) ||
      Date.parse(data.expiresAt) <= Date.now() ||
      vocabularies.some(
        (key) =>
          !Array.isArray(data[key]) ||
          data[key].length === 0 ||
          data[key].length > 128 ||
          new Set(data[key]).size !== data[key].length ||
          data[key].some(
            (item) =>
              typeof item !== "string" || !/^[a-zA-Z0-9_-]{1,128}$/.test(item),
          ),
      ) ||
      JSON.stringify(data.operations) !==
        JSON.stringify(Object.keys(protocol.operations))
    ) {
      fail(
        "SESSION_CONTRACT_INVALID",
        "runtime does not match the packaged authenticated desktop contract",
      );
    }
    this.#session = structuredClone(data);
    this.#epoch = crypto.randomUUID();
    return this.session;
  }

  intent(operation, arguments_) {
    if (!this.connected)
      fail(
        "CONNECTION_REQUIRED",
        "refresh the authenticated runtime before approving an action",
      );
    this.#validateOperation(operation, arguments_);
    return hash(
      JSON.stringify(
        canonical({
          endpoint: this.baseUrl,
          connection: this.#epoch,
          operation,
          arguments: arguments_,
        }),
      ),
    );
  }

  async execute(operation, arguments_ = {}, options = {}) {
    this.#validateOperation(operation, arguments_);
    const mutation = protocol.mutations.includes(operation);
    if (mutation) {
      if (
        !this.connected ||
        typeof options.approval !== "string" ||
        options.approval !== this.intent(operation, arguments_)
      )
        fail(
          "APPROVAL_REQUIRED",
          "approve this exact action on the current authenticated connection",
        );
    } else if (!this.connected) {
      await this.connect({ signal: options.signal });
    }
    const session = this.session;
    const { data, requestId } = await this.#exchange(
      operation,
      arguments_,
      options.signal,
    );
    try {
      this.#validateData(operation, data, arguments_, session);
    } catch (error) {
      if (!(error instanceof DesktopClientError)) throw error;
      throw new DesktopClientError(error.code, error.message, {
        requestId,
        idempotencyKey: arguments_.idempotencyKey,
        uncertain: mutation,
      });
    }
    return data;
  }

  #validateOperation(operation, arguments_) {
    if (
      typeof operation !== "string" ||
      !Object.hasOwn(protocol.operations, operation)
    )
      fail("OPERATION_UNKNOWN", "desktop operation is not declared");
    validate(arguments_, protocol.operations[operation]);
    if (this.#disposed) fail("CLIENT_DISPOSED", "client has been disposed");
    this.assertSafeData(arguments_);
  }

  #validateData(operation, data, arguments_, session) {
    const validRun = (value, quality = false) =>
      record(value) &&
      typeof value.runId === "string" &&
      (quality
        ? /^[a-zA-Z0-9._:-]{1,128}$/.test(value.runId)
        : uuid.test(value.runId)) &&
      (quality ? session.qualityStates : session.runStates).includes(
        value.state,
      );
    let valid = true;
    if (["agents", "teams"].includes(operation))
      valid =
        Array.isArray(data) &&
        data.length <= 256 &&
        data.every(
          (item) =>
            record(item) &&
            typeof item[operation === "agents" ? "agent" : "team"] ===
              "string" &&
            typeof item.name === "string" &&
            typeof item.enabled === "boolean",
        );
    if (operation === "snapshot")
      valid =
        record(data) &&
        uuid.test(data.snapshotId) &&
        hex.test(data.snapshotDigest) &&
        data.manifestDigest === arguments_.manifestDigest &&
        data.trainingAllowed === false &&
        integer(data.fileCount, 1) &&
        data.fileCount === arguments_.files.length &&
        integer(data.sizeBytes, 1);
    if (["lookup", "quality-lookup"].includes(operation))
      valid =
        record(data) &&
        data.idempotencyKey === arguments_.idempotencyKey &&
        typeof data.found === "boolean" &&
        (data.found
          ? validRun(data, operation === "quality-lookup")
          : data.runId === null && data.state === null);
    if (operation === "snapshot-lookup")
      valid =
        record(data) &&
        data.manifestDigest === arguments_.manifestDigest &&
        typeof data.found === "boolean" &&
        (data.found
          ? uuid.test(data.snapshotId) && hex.test(data.snapshotDigest)
          : data.snapshotId === null && data.snapshotDigest === null);
    if (["start", "read", "cancel"].includes(operation))
      valid =
        validRun(data) &&
        (operation === "start" || data.runId === arguments_.runId);
    if (operation === "list")
      valid =
        record(data) &&
        integer(data.total) &&
        Array.isArray(data.runs) &&
        data.runs.length <= (arguments_.limit || 25) &&
        data.runs.every((item) => validRun(item));
    if (
      ["quality-start", "quality-reproduce", "quality-cancel"].includes(
        operation,
      )
    )
      valid =
        validRun(data, true) &&
        (operation !== "quality-cancel" || data.runId === arguments_.runId);
    if (operation === "quality-read")
      valid =
        record(data) &&
        validRun(data.run, true) &&
        data.run.runId === arguments_.runId &&
        Array.isArray(data.checks) &&
        Array.isArray(data.results) &&
        Array.isArray(data.findings) &&
        Array.isArray(data.evidence) &&
        (data.verdict === null ||
          (record(data.verdict) &&
            ["PASS", "FAIL"].includes(data.verdict.verdict)));
    if (["events", "quality-events"].includes(operation)) {
      valid =
        record(data) &&
        Array.isArray(data.events) &&
        data.events.length <= (arguments_.limit || 200) &&
        integer(data.nextCursor) &&
        data.nextCursor >= arguments_.after;
      let cursor = arguments_.after;
      if (valid) {
        for (const event of data.events) {
          if (
            !record(event) ||
            !integer(event.sequence, 1) ||
            event.sequence <= cursor ||
            typeof event[operation === "events" ? "type" : "eventType"] !==
              "string"
          )
            valid = false;
          cursor = event.sequence;
        }
        valid = valid && data.nextCursor === cursor;
      }
    }
    if (!valid) {
      this.#session = null;
      this.#epoch = null;
      fail(
        "RESPONSE_CONTRACT_INVALID",
        "runtime response is inconsistent with its declared identity, state or cursor",
      );
    }
  }

  async #exchange(operation, arguments_, signal) {
    this.#validateOperation(operation, arguments_);
    const requestId = crypto.randomUUID();
    const body = Buffer.from(
      JSON.stringify({
        version: protocol.version,
        requestId,
        operation,
        arguments: arguments_,
      }),
    );
    if (body.length > protocol.maxRequestBytes)
      fail("REQUEST_TOO_LARGE", "request exceeds the protocol byte bound");
    if (signal?.aborted)
      fail(
        "OBSERVATION_CANCELLED",
        "local observation stopped; no remote cancellation is implied",
      );
    const timestamp = String(Math.floor(Date.now() / 1000));
    const signature = mac(
      this.#key,
      [
        protocol.version,
        requestId,
        timestamp,
        "POST",
        protocol.path,
        hash(body),
      ].join("\n"),
    );
    const context = {
      requestId,
      idempotencyKey: arguments_.idempotencyKey,
      uncertain: protocol.mutations.includes(operation),
    };
    return new Promise((resolve, reject) => {
      let settled = false;
      let timer;
      const req = http.request(`${this.baseUrl}${protocol.path}`, {
        method: "POST",
        agent: false,
        headers: {
          "Content-Type": "application/json",
          "Content-Length": body.length,
          Accept: "application/json",
          [protocol.headers.requestId]: requestId,
          [protocol.headers.timestamp]: timestamp,
          [protocol.headers.signature]: signature,
        },
      });
      this.#requests.add(req);
      const finish = (error, value) => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        signal?.removeEventListener("abort", abort);
        this.#requests.delete(req);
        if (error) {
          this.#session = null;
          this.#epoch = null;
          req.destroy();
          reject(error);
        } else resolve(value);
      };
      const abort = () =>
        finish(
          new DesktopClientError(
            "OBSERVATION_CANCELLED",
            "local observation stopped; remote outcome must be reconciled",
            context,
          ),
        );
      signal?.addEventListener("abort", abort, { once: true });
      timer = setTimeout(
        () =>
          finish(
            new DesktopClientError(
              "TRANSPORT_TIMEOUT",
              "runtime deadline elapsed; inspect the stable request identity before another mutation",
              context,
            ),
          ),
        protocol.requestTimeoutSeconds * 1000,
      );
      req.on("error", () =>
        finish(
          new DesktopClientError(
            "TRANSPORT_UNAVAILABLE",
            "runtime connection failed; no automatic mutation retry was performed",
            context,
          ),
        ),
      );
      req.on("response", (res) => {
        let total = 0;
        const parts = [];
        res.on("aborted", () =>
          finish(
            new DesktopClientError(
              "RESPONSE_TRUNCATED",
              "runtime response was interrupted",
              context,
            ),
          ),
        );
        res.on("error", () =>
          finish(
            new DesktopClientError(
              "RESPONSE_TRUNCATED",
              "runtime response could not be read",
              context,
            ),
          ),
        );
        res.on("data", (part) => {
          total += part.length;
          if (total > protocol.maxResponseBytes) {
            finish(
              new DesktopClientError(
                "RESPONSE_TOO_LARGE",
                "runtime response exceeds its byte bound",
                context,
              ),
            );
            res.destroy();
          } else parts.push(part);
        });
        res.on("end", () => {
          if (settled) return;
          const bytes = Buffer.concat(parts);
          const expected = mac(
            this.#key,
            [
              protocol.version,
              requestId,
              String(res.statusCode),
              hash(bytes),
            ].join("\n"),
          );
          if (
            !sameSignature(
              expected,
              res.headers[protocol.headers.signature.toLowerCase()],
            )
          ) {
            finish(
              new DesktopClientError(
                "RESPONSE_AUTHENTICATION_INVALID",
                "runtime response authentication failed; redirects and legacy endpoints are not accepted",
                context,
              ),
            );
            return;
          }
          let parsed;
          try {
            parsed = JSON.parse(
              new TextDecoder("utf-8", { fatal: true }).decode(bytes),
            );
          } catch {
            finish(
              new DesktopClientError(
                "RESPONSE_JSON_INVALID",
                "runtime response is not valid UTF-8 JSON",
                context,
              ),
            );
            return;
          }
          try {
            this.assertSafeData(parsed);
          } catch (error) {
            finish(
              new DesktopClientError(
                error instanceof DesktopClientError
                  ? error.code
                  : "RESPONSE_JSON_INVALID",
                "runtime response failed the protected data or complexity boundary",
                context,
              ),
            );
            return;
          }
          if (res.statusCode < 200 || res.statusCode >= 300) {
            const code =
              typeof parsed?.code === "string" &&
              /^[A-Z][A-Z0-9_]{0,100}$/.test(parsed.code)
                ? parsed.code
                : "REMOTE_ERROR";
            // Only authenticated, canonically declared pre-effect refusals prove no domain
            // mutation happened. Other errors remain uncertain, including signed 5xx failures.
            const refusal = {
              ...context,
              uncertain:
                context.uncertain &&
                !protocol.preEffectRefusalCodes.includes(code),
            };
            finish(
              new DesktopClientError(
                code,
                `runtime refused the request (${code}); reconcile uncertain work before retrying`,
                refusal,
              ),
            );
            return;
          }
          if (
            !record(parsed) ||
            Object.keys(parsed).sort().join(",") !==
              "data,operation,requestId,version" ||
            parsed.version !== protocol.version ||
            parsed.requestId !== requestId ||
            parsed.operation !== operation
          ) {
            finish(
              new DesktopClientError(
                "RESPONSE_ENVELOPE_INVALID",
                "runtime response identity or version does not match the request",
                context,
              ),
            );
            return;
          }
          finish(null, { data: parsed.data, requestId });
        });
      });
      req.end(body);
    });
  }

  dispose() {
    this.#disposed = true;
    this.#session = null;
    this.#epoch = null;
    for (const request of this.#requests) request.destroy();
    this.#requests.clear();
    this.#key = "";
  }
}

module.exports = {
  DesktopClient,
  DesktopClientError,
  protocol,
  protocolDigest,
  endpoint,
  validate,
  hash,
  mac,
  protectData,
};
