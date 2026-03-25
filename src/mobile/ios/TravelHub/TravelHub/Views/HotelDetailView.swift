//
//  HotelDetailView.swift
//  TravelHub
//
//  Created by Andres Donoso on 23/03/26.
//

import SwiftUI

struct HotelDetailView: View {
    var hotel: Hotel

    @State private var aboutLineLimit: Int? = 5
    @State private var readMoreArrow = "chevron.down"
    @State private var showAllAmenities = false

    var featuredAmenities: [HotelAmenity] {
        hotel.amenidades.filter({ $0.isFeatured })
    }

    var topAmenities: [HotelAmenity] {
        if showAllAmenities {
            return hotel.amenidades
        }

        return Array(hotel.amenidades[..<4])
    }

    var body: some View {
        ScrollView(.vertical) {
            VStack(alignment: .leading, spacing: 32) {
                TabView {
                    ForEach(hotel.images, id: \.self) { imageURL in
                        AsyncImage(url: URL(string: imageURL)) { image in
                            image
                                .resizable()
                                .scaledToFill()
                        } placeholder: {
                            ProgressView()
                        }
                    }  //: ForEach
                }  //: TabView Images
                .tabViewStyle(.page)
                .frame(height: 300)

                VStack(alignment: .leading, spacing: 32) {
                    VStack(alignment: .leading, spacing: 16) {
                        HStack(spacing: 4) {
                            Image(systemName: "star")

                            Text("\(hotel.ranking)")
                        }  //: HStack Ranking
                        .foregroundStyle(.accent)

                        Text(hotel.nombre)
                            .font(.title)
                            .bold()

                        HStack(spacing: 4) {
                            Image(systemName: "mappin.and.ellipse")

                            Text("\(hotel.ciudad), \(hotel.pais)")
                                .underline()
                        }  //: HStack Location
                        .foregroundStyle(.neutral)
                    }  //: VStack Hotel Info

                    ScrollView(.horizontal) {
                        HStack {
                            ForEach(featuredAmenities, id: \.self) { amenity in
                                HStack {
                                    Image(systemName: amenity.icon)
                                        .resizable()
                                        .imageScale(.large)
                                        .scaledToFit()
                                        .frame(width: 20, height: 20)

                                    Text(amenity.localizedName)
                                        .frame(maxWidth: .infinity)
                                }  //: HStack Capsule
                                .padding()
                                .background {
                                    Capsule()
                                        .fill(Color.accentLight.opacity(0.4))
                                        .stroke(Color.accentColor, lineWidth: 1)
                                }
                                .padding(.vertical)
                                .foregroundStyle(.accent)
                            }  //: ForEach
                        }  //: HStack
                    }  //: ScrollView Featured Amenities

                    VStack(alignment: .leading, spacing: 16) {
                        Text(LocalizedStringResource.HotelDetail.about)
                            .font(.title2)
                            .bold()

                        Text(hotel.descripcion)
                            .lineLimit(aboutLineLimit)

                        Button {
                            withAnimation {
                                if aboutLineLimit != nil {
                                    aboutLineLimit = nil
                                    readMoreArrow = "chevron.up"
                                } else {
                                    aboutLineLimit = 5
                                    readMoreArrow = "chevron.down"
                                }
                            }
                        } label: {
                            HStack {
                                Text(
                                    LocalizedStringResource.HotelDetail.readMore
                                )
                                .bold()

                                Image(systemName: readMoreArrow)
                                    .contentTransition(
                                        .symbolEffect(
                                            .replace.magic(
                                                fallback: .downUp.byLayer
                                            ),
                                            options: .nonRepeating
                                        )
                                    )
                            }
                        }  //: Button Read More

                    }  //: VStack About
                    .padding(.bottom, 16)

                    VStack(alignment: .leading, spacing: 16) {
                        Text(LocalizedStringResource.HotelDetail.topAmenities)
                            .font(.title2)
                            .bold()

                        LazyVGrid(
                            columns: [.init(.flexible()), .init(.flexible())],
                            alignment: .leading,
                            spacing: 32
                        ) {
                            ForEach(self.topAmenities, id: \.self) { amenity in
                                HStack(spacing: 16) {
                                    Image(systemName: amenity.icon)
                                        .resizable()
                                        .scaledToFit()
                                        .frame(width: 25, height: 25)

                                    Text(amenity.localizedName)
                                }  //: HStack Amenity
                            }  //: ForEach
                        }  //: LazyVGrid Amenities

                        Button {
                            withAnimation {
                                showAllAmenities.toggle()
                            }
                        } label: {
                            Spacer()

                            Text(
                                showAllAmenities
                                    ? LocalizedStringResource.HotelDetail
                                        .showLess
                                    : LocalizedStringResource.HotelDetail
                                        .showAllAmenities(
                                            numAmenities: hotel.amenidades.count
                                        )
                            )
                            .foregroundStyle(.black)
                            .bold()

                            Spacer()
                        }  //: Button Show All
                        .padding()
                        .overlay {
                            Capsule()
                                .stroke(Color.neutralLight, lineWidth: 1)
                        }

                    }  //: VStack Top Amenities

                }  //: VStack Hotel Data Container
                .padding(.horizontal)

                Spacer()
            }  //: VStack Container
            .background(Color.formBackground)
            .padding(.bottom, 48)
        }  // ScrollView
        .ignoresSafeArea(edges: .top)
        .padding(.bottom, 30)
        .overlay(alignment: .bottom) {
            UnevenRoundedRectangle(topLeadingRadius: 25, topTrailingRadius: 25)
                .fill(.background)
                .frame(height: 100)
                .shadow(color: .black.opacity(0.15), radius: 10)
            
            HStack {
                VStack(alignment: .leading) {
                    HStack {
                        // TODO: Change this for value of room
                        Text(480_000.formatted(.currency(code: "COP")))
                            .font(.title3)
                            .bold()
                        
                        Text(LocalizedStringResource.HotelDetail.perNight)
                            .foregroundStyle(.neutral)
                    } //: HStack Price
                    
                    Text(LocalizedStringResource.HotelDetail.freeCancellation)
                        .font(.caption)
                        .foregroundStyle(.accent)
                        .bold()
                } //: VStack
                
                Spacer()
                
                Button {
                    // TODO: Book reservation
                } label: {
                    Text(LocalizedStringResource.HotelDetail.bookNow)
                        .bold()
                        .foregroundStyle(.white)
                        .padding(.horizontal, 32)
                }
                .capsuleButton()
                
            } //: HStack
            .padding(.horizontal, 32)
        } //: Overlay Book Now
        .ignoresSafeArea()
        .toolbar(.hidden, for: .tabBar)
    }
}

#Preview {
    HotelDetailView(
        hotel: Hotel(
            id: 1,
            nombre: "Grand Hotel",
            direccion: "123 Fifth Ave",
            pais: "United States",
            estado: "New York",
            departamento: "Manhattan",
            ciudad: "New York City",
            descripcion:
                "Nestled in the heart of Manhattan, the Grand Hotel offers an unparalleled luxury experience steps away from Central Park, Fifth Avenue, and the city's most iconic landmarks. Our elegantly appointed rooms blend classic New York sophistication with modern comforts, ensuring every stay is nothing short of extraordinary.\n\nWhether you're here for business or leisure, our world-class amenities — including a rooftop pool, award-winning spa, and Michelin-starred restaurant — are designed to exceed every expectation. Let our dedicated concierge team craft your perfect New York City experience from the moment you arrive.",
            amenidades: [
                .airConditioning, .bar, .pool, .petFriendly, .gym, .laundry,
                .breakfastIncluded,
            ],
            ranking: 4,
            contactoCelular: "+1 212 000 0001",
            contactoEmail: "contact@grandhotel.com",
            images: [
                "https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg",
                "https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg",
            ],
            checkInHour: "15:00",
            checkOutHour: "11:00",
            valorMinimoModificacion: 250
        )
    )
}
