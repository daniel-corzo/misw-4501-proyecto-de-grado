//
//  HotelDetailView.swift
//  TravelHub
//
//  Created by Andres Donoso on 23/03/26.
//

import SwiftUI

struct HotelDetailView: View {
    var hotel: Hotel

    var body: some View {
        Text( /*@START_MENU_TOKEN@*/"Hello, World!" /*@END_MENU_TOKEN@*/)
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
            descripcion: "A luxurious hotel in the heart of New York City.",
            amenidades: "Pool, Gym, Spa, Restaurant",
            ranking: 4,
            contactoCelular: "+1 212 000 0001",
            contactoEmail: "contact@grandhotel.com",
            images: [
                "https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg"
            ],
            checkInHour: "15:00",
            checkOutHour: "11:00",
            valorMinimoModificacion: 250,
            title: "Grand Hotel",
            imageURL:
                "https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg",
            location: "New York",
            price: "$250",
            rating: 4
        )
    )
}
