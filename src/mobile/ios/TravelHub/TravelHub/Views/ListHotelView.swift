//
//  ListHotelView.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 22/03/26.
//

import SwiftUI

struct ListHotelView: View {
    @StateObject private var viewModel = ListHotelViewModel()
    @State private var searchText: String = ""
    @State private var filterIsActive = false
    @State private var showFilterSheet = false
    
    // Hoteles filtrados según búsqueda
    var filteredHotels: [Hotel] {
        if searchText.isEmpty {
            return viewModel.hotels
        } else {
            return viewModel.hotels.filter {
                $0.location.localizedCaseInsensitiveContains(searchText) ||
                $0.title.localizedCaseInsensitiveContains(searchText)
            }
        }
    }
    
    var body: some View {
        VStack(spacing: 16) {
            Text("Hotels")
                .font(.title3)
                .fontWeight(.bold)
                .frame(maxWidth: .infinity, alignment: .center)
            
            // Barra de búsqueda
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
            
            // Barra de filtros y orden
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
                        // Aquí va la vista de filtros
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
            
            // Lista de hoteles filtrada
            ScrollView {
                LazyVStack(spacing: 24) {
                    ForEach(filteredHotels) { hotel in
                        ListElementView(
                            imageURL: hotel.imageURL,
                            title: hotel.title,
                            location: hotel.location,
                            price: hotel.price,
                            rating: hotel.rating
                        )
                        .padding(.horizontal)
                    }
                }
                .padding(.top)
            }
        }
    }
    
}

#Preview {
    ListHotelView()
}
