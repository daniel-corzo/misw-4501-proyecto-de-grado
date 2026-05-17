//
//  MyBookingsView.swift
//  TravelHub
//

import SwiftUI

struct MyBookingsView: View {
    @Environment(\.bookingService) private var bookingService
    @Environment(\.toastManager) private var toastManager
    @Environment(Router.self) private var router

    @State private var viewModel = ViewModel()

    var body: some View {
        VStack(spacing: 0) {
            // MARK: - Tab Picker
            HStack(spacing: 0) {
                ForEach(BookingTab.allCases, id: \.self) { tab in
                    Button {
                        withAnimation(.easeInOut(duration: 0.2)) {
                            viewModel.selectedTab = tab
                        }
                    } label: {
                        VStack(spacing: 8) {
                            Text(tab.title)
                                .font(.subheadline)
                                .fontWeight(viewModel.selectedTab == tab ? .semibold : .regular)
                                .foregroundStyle(
                                    viewModel.selectedTab == tab ? .blue : .gray
                                )

                            Rectangle()
                                .fill(viewModel.selectedTab == tab ? Color.blue : Color.clear)
                                .frame(height: 2)
                        }
                    }
                    .frame(maxWidth: .infinity)
                }
            }
            .padding(.horizontal)
            .padding(.top, 8)

            Divider()

            // MARK: - Content
            if viewModel.isLoading {
                Spacer()
                ProgressView()
                Spacer()
            } else if viewModel.hasError {
                errorStateView
            } else if viewModel.bookings.isEmpty {
                emptyStateView
            } else {
                bookingsList
            }
        }
        .navigationTitle(LocalizedStringResource.MyBookings.navigationTitle)
        .navigationBarTitleDisplayMode(.inline)
        .task(id: viewModel.selectedTab) {
            if let pending = router.pendingBookingTab {
                router.pendingBookingTab = nil
                viewModel.selectedTab = pending
                return
            }
            viewModel.bookingService = bookingService
            viewModel.toastManager = toastManager
            await viewModel.fetchBookings()
        }
    }

    // MARK: - Bookings List

    private var bookingsList: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 16) {
                // Section header
                VStack(alignment: .leading, spacing: 4) {
                    Text(viewModel.selectedTab.sectionTitle)
                        .font(.title3)
                        .fontWeight(.bold)

                    Text(viewModel.selectedTab.bookingCountMessage(viewModel.bookings.count))
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                .padding(.horizontal, 4)

                // Cards
                ForEach(viewModel.bookings) { booking in
                    BookingCardView(booking: booking)
                }
            }
            .padding(.horizontal, 20)
            .padding(.top, 20)
            .padding(.bottom, 24)
        }
    }

    // MARK: - Empty State

    private var emptyStateView: some View {
        VStack(spacing: 16) {
            Spacer()
            Image(systemName: "calendar.badge.exclamationmark")
                .resizable()
                .scaledToFit()
                .frame(width: 64, height: 64)
                .foregroundStyle(.gray.opacity(0.5))

            Text(viewModel.selectedTab.emptyMessage)
                .font(.body)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
            Spacer()
        }
    }

    // MARK: - Error State

    private var errorStateView: some View {
        VStack(spacing: 16) {
            Spacer()
            Image(systemName: "exclamationmark.triangle")
                .resizable()
                .scaledToFit()
                .frame(width: 56, height: 56)
                .foregroundStyle(.orange)

            Text(LocalizedStringResource.MyBookings.errorGeneric)
                .font(.body)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)

            Button {
                Task {
                    await viewModel.fetchBookings()
                }
            } label: {
                Text(LocalizedStringResource.MyBookings.retry)
                    .fontWeight(.semibold)
                    .foregroundStyle(.white)
                    .padding(.horizontal, 32)
                    .padding(.vertical, 12)
                    .background(Color.blue)
                    .clipShape(Capsule())
            }
            Spacer()
        }
    }
}

#Preview {
    NavigationStack {
        MyBookingsView()
    }
}
