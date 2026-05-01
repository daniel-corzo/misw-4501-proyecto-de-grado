//
//  ListElementView.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 22/03/26.
//

import SwiftUI

struct ListElementView: View {
    
    @Environment(Router.self) private var router
    
    var id: UUID
    var imageURL: String
    var title: String
    var location: String
    var price: String
    var rating: Int
    var fetchHotelDetail: () async -> Hotel?
    
    var body: some View {
        VStack(spacing: 0) {
            
            // MARK: - Imagen desde URL con placeholder
            AsyncImage(url: URL(string: imageURL)) { phase in
                switch phase {
                case .empty:
                    // Placeholder mientras carga
                    ZStack {
                        Color.gray.opacity(0.2)
                        ProgressView()
                    }
                    .frame(height: 220)
                    .frame(maxWidth: .infinity)
                    
                case .success(let image):
                    Color.clear
                        .frame(maxWidth: .infinity)
                        .frame(height: 220)
                        .overlay {
                            image
                                .resizable()
                                .scaledToFill()
                        }
                        .clipped()
                    
                case .failure:
                    // Imagen fallback si falla
                    ZStack {
                        Color.gray.opacity(0.2)
                        Image(systemName: "photo")
                            .resizable()
                            .scaledToFit()
                            .foregroundColor(.gray)
                            .padding(40)
                    }
                    .frame(height: 220)
                    .frame(maxWidth: .infinity)
                    
                @unknown default:
                    EmptyView()
                }
            }
            
            // MARK: - Contenido
            VStack(alignment: .leading, spacing: 2) {
                
                HStack {
                    Text(title)
                        .font(.title3)
                        .fontWeight(.bold)
                    
                    Spacer()
                    
                    HStack(spacing: 4) {
                        Image(systemName: "star.fill")
                        Text("\(rating)")
                            .fontWeight(.semibold)
                    }
                    .font(.footnote)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(Color.blue.opacity(0.1))
                    .foregroundStyle(.blue)
                    .clipShape(Capsule())
                }
                
                Text(location)
                    .font(.subheadline)
                    .foregroundStyle(.gray)
                
                HStack {
                    HStack(alignment: .firstTextBaseline, spacing: 4) {
                        Text(price)
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        Text(LocalizedStringResource.HotelList.perNight)
                            .foregroundStyle(.gray)
                    }
                    
                    Spacer()
                    
                    Button {
                        Task {
                            if let hotel = await fetchHotelDetail() {
                                router.navigate(to: .createBooking(hotel, nil))
                            }
                        }
                    } label: {
                        Text(LocalizedStringResource.HotelList.bookNow)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                            .padding(.horizontal, 24)
                            .padding(.vertical, 12)
                            .background(Color.blue)
                            .clipShape(Capsule())
                    }
                }
            }
            .padding()
            .background(Color(.systemGray6))
        }
        .clipShape(RoundedRectangle(cornerRadius: 30))
        .shadow(color: .black.opacity(0.15), radius: 20, y: 10)
    }
}

#Preview {
    let habitaciones = [
        Habitacion(
            id: UUID(),
            capacidad: 2,
            numero: "101",
            descripcion:
                "Comfortable room with a stunning city view and king-size bed.",
            imagenes: [
                "https://cf.bstatic.com/xdata/images/hotel/max1024x768/837215020.jpg"
            ],
            monto: 420000,
            impuestos: 80000,
            disponible: true
        ),
        Habitacion(
            id: UUID(),
            capacidad: 3,
            numero: "202",
            descripcion:
                "Spacious deluxe suite with separate living area and panoramic views.",
            imagenes: [
                "https://www.maritim.com/fileadmin/_processed_/0/1/csm_Bpa_363_Superior_500a005b62.jpg"
            ],
            monto: 450000,
            impuestos: 90000,
            disponible: true
        ),
        Habitacion(
            id: UUID(),
            capacidad: 4,
            numero: "301",
            descripcion:
                "Premium suite with private terrace, jacuzzi and butler service.",
            imagenes: [
                "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/2c/29/84/e3/486104-guest-room.jpg"
            ],
            monto: 820000,
            impuestos: 120000,
            disponible: false
        ),
    ]
    
    ListElementView(
        id: UUID(),
        imageURL: "https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg",
        title: "Grand Hyatt Regency",
        location: "San Francisco",
        price: "$250",
        rating: 4,
        fetchHotelDetail: {
            return Hotel(
                id: UUID(),
                nombre: "Grand Plaza Hotel",
                direccion: "Calle 123 # 45-67",
                pais: "Colombia",
                estado: "Cundinamarca",
                departamento: "Cundinamarca",
                ciudad: "Bogotá",
                descripcion:
                    "A luxury hotel in the heart of Bogotá with world-class amenities.",
                amenidades: [
                    .pool, .wifi, .gym, .spa, .parking, .breakfastIncluded,
                ],
                estrellas: 4,
                ranking: 4.7,
                contactoCelular: "+57 300 000 0000",
                contactoEmail: "invalid-email.com",
                images: [],
                checkInHour: "14:00",
                checkOutHour: "12:00",
                valorMinimoModificacion: 100000,
                politicas: [],
                habitaciones: habitaciones,
                precioMinimo: 420000
            )
        }
    )
    .padding()
}
