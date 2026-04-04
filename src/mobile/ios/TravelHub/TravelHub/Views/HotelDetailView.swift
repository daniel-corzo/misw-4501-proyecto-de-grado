//
//  HotelDetailView.swift
//  TravelHub
//
//  Created by Andres Donoso on 23/03/26.
//

import SwiftUI

struct HotelDetailView: View {
    var hotelId: UUID

    @State private var viewModel = ViewModel()
    @State private var aboutLineLimit: Int? = 3
    @State private var readMoreArrow = "chevron.down"
    @State private var showAllAmenities = false
    @State private var descriptionIsTruncated = false

    @Environment(\.toastManager) private var toastManager: ToastManager

    var featuredAmenities: [HotelAmenity] {
        guard let hotel = viewModel.hotel else { return [] }
        return hotel.amenidades.filter({ $0.isFeatured })
    }

    var topAmenities: [HotelAmenity] {
        guard let hotel = viewModel.hotel else { return [] }
        if showAllAmenities {
            return hotel.amenidades
        }
        return Array(hotel.amenidades.prefix(4))
    }

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let hotel = viewModel.hotel {
                hotelContent(hotel)
            }
        }
        .toolbar(.hidden, for: .tabBar)
        .task {
            viewModel.fetchHotelDetail(hotelId: hotelId, toastManager: toastManager)
        }
    }

    @ViewBuilder
    private func hotelContent(_ hotel: Hotel) -> some View {
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

                            Text(String(format: "%.1f", hotel.ranking))
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
                            .background {
                                Text(hotel.descripcion)
                                    .lineLimit(3)
                                    .hidden()
                                    .background {
                                        GeometryReader { visibleGeometry in
                                            Text(hotel.descripcion)
                                                .fixedSize(horizontal: false, vertical: true)
                                                .hidden()
                                                .background {
                                                    GeometryReader { fullGeometry in
                                                        Color.clear.onAppear {
                                                            descriptionIsTruncated = fullGeometry.size.height > visibleGeometry.size.height
                                                        }
                                                    }
                                                }
                                        }
                                    }
                            }

                        if descriptionIsTruncated {
                            Button {
                                withAnimation {
                                    if aboutLineLimit != nil {
                                        aboutLineLimit = nil
                                        readMoreArrow = "chevron.up"
                                    } else {
                                        aboutLineLimit = 3
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
                        }

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

                        if hotel.amenidades.count > 4 {
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
                        if let room = hotel.habitaciones.first {
                            Text(room.monto.formatted(.currency(code: "COP")))
                                .font(.title3)
                                .bold()
                        }

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
    }
}

#Preview {
    HotelDetailView(hotelId: UUID())
}
