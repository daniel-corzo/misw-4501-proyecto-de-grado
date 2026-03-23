//
//  Hotel.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 23/03/26.
//

import Foundation

struct Hotel: Identifiable, Codable {
    var id: Int
    var nombre: String
    var direccion: String
    var pais: String
    var estado: String
    var departamento: String
    var ciudad: String
    var descripcion: String
    var amenidades: String
    var ranking: Int
    var contactoCelular: String
    var contactoEmail: String
    var images: [String]
    var checkInHour: String
    var checkOutHour: String
    var valorMinimoModificacion: Int
    
    @available(*, deprecated, renamed: "nombre", message: "Use nombre instead")
    var title: String
    
    @available(*, deprecated, renamed: "images", message: "Use images array instead")
    var imageURL: String
    
    @available(*, deprecated, renamed: "ciudad", message: "Use ciudad instead")
    var location: String
    
    @available(*, deprecated, renamed: "valorMinimoModificacion", message: "Use valorMinimoModificacion instead")
    var price: String
    
    @available(*, deprecated, renamed: "ranking", message: "Use ranking instead")
    var rating: Int
}
