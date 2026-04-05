//
//  ProfileView.swift
//  TravelHub
//

import SwiftUI

struct ProfileView: View {

    @Environment(\.userService) private var userService: UserService
    @Environment(\.authService) private var authService: AuthService
    @Environment(\.toastManager) private var toastManager: ToastManager

    @State private var viewModel = ViewModel()

    @Binding var isLoggedIn: Bool

    var body: some View {
        ZStack {
            Color.formBackground
                .ignoresSafeArea()

            if viewModel.isLoading {
                ProgressView()
            } else {
                ScrollView {
                    VStack(spacing: 24) {

                        // MARK: - Avatar + Name
                        VStack(spacing: 12) {
                            Image(systemName: "person.crop.circle.fill")
                                .resizable()
                                .scaledToFit()
                                .frame(width: 90, height: 90)
                                .foregroundStyle(.gray.opacity(0.6))

                            Text(viewModel.userName)
                                .font(.title2)
                                .fontWeight(.bold)
                        }
                        .padding(.top, 8)

                        // MARK: - Account Overview
                        ProfileSectionView(header: "ACCOUNT OVERVIEW") {
                            ProfileRowView(icon: "person", title: "Personal Information")
                            Divider().padding(.leading, 48)
                            ProfileRowView(
                                icon: "clock.arrow.circlepath",
                                title: "Booking History",
                                subtitle: "View your past stays"
                            )
                            Divider().padding(.leading, 48)
                            ProfileRowView(icon: "creditcard", title: "Payment Methods")
                        }

                        // MARK: - Preferences
                        ProfileSectionView(header: "PREFERENCES") {
                            ProfileRowView(icon: "bell", title: "Notifications")
                            Divider().padding(.leading, 48)
                            ProfileRowView(icon: "lock.shield", title: "Privacy & Security")
                            Divider().padding(.leading, 48)
                            ProfileRowView(icon: "questionmark.circle", title: "Support & FAQ")
                        }

                        // MARK: - Log Out
                        Button {
                            Task {
                                do {
                                    try await viewModel.logOut()
                                    isLoggedIn = false
                                } catch {
                                    toastManager.error(error.localizedDescription)
                                }
                            }
                        } label: {
                            HStack {
                                Image(systemName: "rectangle.portrait.and.arrow.right")
                                Text("Log Out")
                                    .fontWeight(.semibold)
                            }
                            .foregroundStyle(.red)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(Color.red.opacity(0.08))
                            )
                        }
                        .padding(.horizontal)

                        // MARK: - Footer
                        Text("TravelHub")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                            .padding(.bottom, 8)
                    }
                    .padding(.vertical)
                }
            }
        }
        .navigationTitle("Profile")
        .navigationBarTitleDisplayMode(.inline)
        .task {
            viewModel.userService = userService
            viewModel.authService = authService
            await viewModel.fetchProfile(toastManager: toastManager)
        }
    }
}

// MARK: - Profile Section

private struct ProfileSectionView<Content: View>: View {
    let header: String
    @ViewBuilder let content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Text(header)
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundStyle(.secondary)
                .padding(.horizontal)
                .padding(.bottom, 8)

            VStack(spacing: 0) {
                content
            }
            .padding(.vertical, 4)
            .background(
                RoundedRectangle(cornerRadius: 14)
                    .fill(Color(.systemBackground))
            )
            .padding(.horizontal)
        }
    }
}

// MARK: - Profile Row

private struct ProfileRowView: View {
    let icon: String
    let title: String
    var subtitle: String? = nil

    var body: some View {
        HStack(spacing: 14) {
            Image(systemName: icon)
                .font(.body)
                .foregroundStyle(.primary)
                .frame(width: 24)

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.body)

                if let subtitle {
                    Text(subtitle)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            Spacer()

            Image(systemName: "chevron.right")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding(.horizontal)
        .padding(.vertical, 12)
        .contentShape(Rectangle())
    }
}

#Preview {
    NavigationStack {
        ProfileView(isLoggedIn: .constant(true))
    }
}
