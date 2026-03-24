//
//  ListHotel+ViewModel.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 23/03/26.
//

import Foundation
import Combine
import SwiftUI

class ListHotelViewModel: ObservableObject {
    @Published var hotels: [Hotel] = []
    
    init() {
        fetchHotels()
    }
    
    func fetchHotels() {
        // Simula llamada a API con retraso
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            self.hotels = [
                Hotel(
                    id: 1,
                    nombre: "Grand Hotel",
                    direccion: "123 Fifth Ave",
                    pais: "United States",
                    estado: "New York",
                    departamento: "Manhattan",
                    ciudad: "New York City",
                    descripcion: "A luxurious hotel in the heart of New York City.",
                    amenidades: [.airConditioning, .bar, .pool, .petFriendly, .gym, .laundry, .breakfastIncluded],
                    ranking: 4,
                    contactoCelular: "+1 212 000 0001",
                    contactoEmail: "contact@grandhotel.com",
                    images: ["https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg"],
                    checkInHour: "15:00",
                    checkOutHour: "11:00",
                    valorMinimoModificacion: 250,
                    title: "Grand Hotel",
                    imageURL: "https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg",
                    location: "New York",
                    price: "$250",
                    rating: 4
                ),
                Hotel(
                    id: 2,
                    nombre: "Ocean View",
                    direccion: "456 Ocean Drive",
                    pais: "United States",
                    estado: "Florida",
                    departamento: "Miami-Dade",
                    ciudad: "Miami",
                    descripcion: "Beautiful beachfront hotel with stunning ocean views.",
                    amenidades: [.airConditioning, .bar, .pool, .petFriendly, .gym, .laundry, .breakfastIncluded],
                    ranking: 5,
                    contactoCelular: "+1 305 000 0002",
                    contactoEmail: "contact@oceanview.com",
                    images: ["https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg"],
                    checkInHour: "14:00",
                    checkOutHour: "12:00",
                    valorMinimoModificacion: 180,
                    title: "Ocean View",
                    imageURL: "https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg",
                    location: "Miami",
                    price: "$180",
                    rating: 5
                ),
                Hotel(
                    id: 3,
                    nombre: "Mountain Retreat",
                    direccion: "789 Mountain Rd",
                    pais: "United States",
                    estado: "Colorado",
                    departamento: "Denver County",
                    ciudad: "Denver",
                    descripcion: "A peaceful retreat surrounded by the Rocky Mountains.",
                    amenidades: [.airConditioning, .bar, .pool, .petFriendly, .gym, .laundry, .breakfastIncluded],
                    ranking: 4,
                    contactoCelular: "+1 720 000 0003",
                    contactoEmail: "contact@mountainretreat.com",
                    images: ["https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg"],
                    checkInHour: "15:00",
                    checkOutHour: "11:00",
                    valorMinimoModificacion: 200,
                    title: "Mountain Retreat",
                    imageURL: "https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg",
                    location: "Denver",
                    price: "$200",
                    rating: 4
                )
            ]
        }
    }
}
