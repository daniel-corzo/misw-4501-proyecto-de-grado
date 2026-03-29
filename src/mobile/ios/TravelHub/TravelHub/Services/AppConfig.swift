import Foundation

/// Central configuration for app-wide constants.
enum AppConfig {
    // Base URL for the backend API (no trailing slash). Example test URL shown below.
    static let apiBaseURL = URL(string: "http://localhost:8080/api/auth")!
}
