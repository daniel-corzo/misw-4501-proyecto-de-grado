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
    @State private var filterIsActive = false
    @State private var showFilterSheet = false
    
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
            
            Text("Hotels")
                .font(.title3)
                .fontWeight(.bold)
                .frame(maxWidth: .infinity)
            
            // 🔍 Search
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
            .padding(.horizontal)
            
            // 🎛️ Filtros
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    
                    Button {
                        filterIsActive.toggle()
                        showFilterSheet = true
                    } label: {
                        Label(LocalizedStringResource.HotelList.filter, systemImage: "slider.horizontal.3")
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(filterIsActive ? Color.blue : Color(.systemGray5))
                            .foregroundColor(filterIsActive ? .white : .gray)
                            .clipShape(Capsule())
                    }
                    .sheet(isPresented: $showFilterSheet) {
                        Text("Filter options here")
                            .presentationDetents([.medium])
                    }
                    
                    Button(LocalizedStringResource.HotelList.sort) {
                        // Acción sort
                    }
                    .buttonStyle(.bordered)
                    
                    Button(LocalizedStringResource.HotelList.price) {
                        // Acción price
                    }
                    .buttonStyle(.bordered)
                    
                    Button(LocalizedStringResource.HotelList.rating) {
                        // Acción rating
                    }
                    .buttonStyle(.bordered)
                }
                .padding(.horizontal)
            }
            
            // 🏨 Lista
            ScrollView {
                LazyVStack(spacing: 24) {
                    ForEach(filteredHotels) { hotel in
                        
                        NavigationLink {
                            HotelDetailView(hotel: hotel)
                        } label: {
                            ListElementView(
                                imageURL: hotel.images[0],
                                title: hotel.nombre,
                                location: hotel.ciudad,
                                price: "100",
                                rating: hotel.ranking
                            )
                        }
                        .buttonStyle(.plain)
                        .padding(.horizontal)
                    }
                }
                .padding(.top)
                .padding(.bottom, 100)
            }
        }
    }
}

#Preview {
    ListHotelView()
}
