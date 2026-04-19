//
//  ListElementView.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 22/03/26.
//

import SwiftUI

struct ListElementView: View {
    
    var imageURL: String
    var title: String
    var location: String
    var price: String
    var rating: Int
    
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
                        // TODO: Book reservation
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
    ListElementView(
        imageURL: "https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg",
        title: "Grand Hyatt Regency",
        location: "San Francisco",
        price: "$250",
        rating: 4
    )
    .padding()
}
