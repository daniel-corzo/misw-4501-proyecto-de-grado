//
//  ListHotelView.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 22/03/26.
//

import SwiftUI

struct ListHotelView: View {
    @State private var viewModel = ViewModel()
    @State private var searchText: String = ""
    @State private var showFilterSheet = false

    @Environment(\.toastManager) private var toastManager: ToastManager
    @Environment(Router.self) private var router

    var filteredHotels: [Hotel] {
        if searchText.isEmpty {
            return viewModel.hotels
        } else {
            return viewModel.hotels.filter {
                $0.ciudad.localizedCaseInsensitiveContains(searchText) ||
                $0.nombre.localizedCaseInsensitiveContains(searchText)
            }
        }
    }

    var body: some View {
        VStack(spacing: 16) {
            Text(LocalizedStringResource.HotelList.screenName)
                .font(.title3)
                .fontWeight(.bold)
                .frame(maxWidth: .infinity)

            // Search + Filter
            HStack(spacing: 10) {
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(.gray)
                    TextField(LocalizedStringResource.HotelList.searchMessage, text: $searchText)
                        .textInputAutocapitalization(.never)
                        .disableAutocorrection(true)
                }
                .padding(10)
                .background(Color(.systemGray6))
                .cornerRadius(12)

                Button {
                    showFilterSheet = true
                } label: {
                    Image(systemName: "slider.horizontal.3")
                        .font(.title3)
                        .padding(10)
                        .background(viewModel.hasActiveFilters ? Color.blue : Color(.systemGray6))
                        .foregroundColor(viewModel.hasActiveFilters ? .white : .gray)
                        .cornerRadius(12)
                }
                .sheet(isPresented: $showFilterSheet) {
                    FilterSortView(viewModel: viewModel) {
                        Task {
                            await viewModel.fetchHotels(toastManager: toastManager)
                        }
                    }
                    .presentationDragIndicator(.hidden)
                }
            }
            .padding(.horizontal)

            // Hotel list
            ScrollView {
                LazyVStack(spacing: 24) {
                    ForEach(filteredHotels) { hotel in

                        Button {
                            router.navigate(to: .hotelDetail(hotel.id))
                        } label: {
                            ListElementView(
                                id: hotel.id,
                                imageURL: hotel.images.first ?? "",
                                title: hotel.nombre,
                                location: hotel.ciudad,
                                price: (hotel.precioMinimo).formatted(.currency(code: "COP")),
                                rating: hotel.estrellas,
                                fetchHotelDetail: { return await self.viewModel.fetchHotelDetail(hotelId: hotel.id, toastManager: self.toastManager) }
                            )
                        }
                        .buttonStyle(.plain)
                        .padding(.horizontal)
                    }
                }
                .padding(.top)
                .padding(.bottom, 20)
            }
        }
        .task {
            await viewModel.fetchHotels(toastManager: toastManager)
        }
    }

}

#Preview {
    ListHotelView()
}
