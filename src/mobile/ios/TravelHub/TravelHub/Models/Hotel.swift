//
//  Hotel.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 23/03/26.
//

import Foundation

struct Hotel: Identifiable, Codable {
    let id = UUID()               // Identificador único para ForEach
    let imageURL: String          // URL de la imagen
    let title: String             // Nombre del hotel
    let location: String          // Ciudad o ubicación
    let price: String             // Precio por noche
    let rating: Int               // Valoración (1 a 5)
}
