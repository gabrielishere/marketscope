import { ApplicationConfig, InjectionToken, provideZoneChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { ApiConfiguration } from './api/api-configuration';

/**
 * Where the API lives, decided at runtime rather than at build time.
 *
 * **Deployed, the API and this page share an origin** — FastAPI serves the built
 * application at `/` and its routes alongside — so the base URL is empty and every request
 * goes to whatever host served the page. That is what removes CORS from production entirely.
 *
 * **In development they do not.** `ng serve` runs on 4200 and the API on 8000, which is why
 * the backend carries `CORSMiddleware` at all.
 *
 * Decided by looking at the port rather than by a build configuration, because a build flag
 * is a second thing to get right and this has exactly one correct answer in each case.
 */
function apiRootUrl(): string {
  const devServer = typeof window !== 'undefined' && window.location.port === '4200';
  return devServer ? 'http://localhost:8000' : '';
}

export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL', {
  providedIn: 'root',
  factory: apiRootUrl,
});

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(),
    {
      provide: ApiConfiguration,
      useFactory: () => {
        const config = new ApiConfiguration();
        config.rootUrl = apiRootUrl();
        return config;
      },
    },
  ],
};
