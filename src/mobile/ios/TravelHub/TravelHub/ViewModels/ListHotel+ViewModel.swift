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
                    imageURL: "https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg",
                    title: "Grand Hotel",
                    location: "New York",
                    price: "$250",
                    rating: 4
                ),
                Hotel(
                    imageURL: "https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg",
                    title: "Ocean View",
                    location: "Miami",
                    price: "$180",
                    rating: 5
                ),
                Hotel(
                    imageURL: "https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg",
                    title: "Mountain Retreat",
                    location: "Denver",
                    price: "$200",
                    rating: 4
                )
            ]
        }
    }
}
