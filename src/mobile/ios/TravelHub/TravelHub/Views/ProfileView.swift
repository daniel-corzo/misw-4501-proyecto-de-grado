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
        Group {
            if viewModel.isLoading {
                ProgressView()
            } else {
                List {
                    // MARK: - Avatar + Name
                    Section {
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
                        .frame(maxWidth: .infinity)
                        .listRowBackground(Color.clear)
                    }

                    // MARK: - Account Overview
                    Section(LocalizedStringResource.Profile.accountOverview) {
                        Label(LocalizedStringResource.Profile.personalInformation, systemImage: "person")
                        HStack {
                            Label(LocalizedStringResource.Profile.bookingHistory, systemImage: "clock.arrow.circlepath")
                            Spacer()
                            Text(LocalizedStringResource.Profile.viewYourPastStays)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        Label(LocalizedStringResource.Profile.paymentMethods, systemImage: "creditcard")
                    }

                    // MARK: - Preferences
                    Section(LocalizedStringResource.Profile.preferences) {
                        Label(LocalizedStringResource.Profile.notifications, systemImage: "bell")
                        Label(LocalizedStringResource.Profile.privacyAndSecurity, systemImage: "lock.shield")
                        Label(LocalizedStringResource.Profile.supportAndFaq, systemImage: "questionmark.circle")
                    }

                    // MARK: - Log Out
                    Section {
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
                                Text(LocalizedStringResource.Profile.logOut)
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
                        .listRowBackground(Color.clear)
                    }

                    // MARK: - Footer
                    Section {
                        Text("TravelHub")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                            .frame(maxWidth: .infinity)
                            .listRowBackground(Color.clear)
                    }
                }
                .listStyle(.insetGrouped)
            }
        }
        .navigationTitle(LocalizedStringResource.Profile.title)
        .navigationBarTitleDisplayMode(.inline)
        .task {
            viewModel.userService = userService
            viewModel.authService = authService
            await viewModel.fetchProfile(toastManager: toastManager)
        }
    }
}

#Preview {
    NavigationStack {
        ProfileView(isLoggedIn: .constant(true))
    }
}
