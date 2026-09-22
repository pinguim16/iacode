/**
 * The application shell.
 *
 * It identifies the product and offers the two pages this build has. It reads nothing and renders
 * no state of its own, so a page that fails to load leaves the navigation working — which is how
 * somebody discovers that the other page still answers.
 */

import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {}
