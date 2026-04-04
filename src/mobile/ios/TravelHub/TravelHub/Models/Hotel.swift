//
//  Hotel.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 23/03/26.
//

import Foundation

enum HotelAmenity: String, Codable {
    case pool = "POOL"
    case gym = "GYM"
    case spa = "SPA"
    case restaurant = "RESTAURANT"
    case bar = "BAR"
    case wifi = "WIFI"
    case parking = "PARKING"
    case airConditioning = "AIR_CONDITIONING"
    case roomService = "ROOM_SERVICE"
    case laundry = "LAUNDRY"
    case concierge = "CONCIERGE"
    case beachAccess = "BEACH_ACCESS"
    case skiAccess = "SKI_ACCESS"
    case petFriendly = "PET_FRIENDLY"
    case smokingArea = "SMOKING_AREA"
    case evCharging = "EV_CHARGING"
    case businessCenter = "BUSINESS_CENTER"
    case conferenceRoom = "CONFERENCE_ROOM"
    case childrenPlayground = "CHILDREN_PLAYGROUND"
    case shuttle = "SHUTTLE"
    case breakfastIncluded = "BREAKFAST_INCLUDED"
    
    var localizedName: LocalizedStringResource {
        switch self {
            case .pool: return .HotelAmenities.pool
            case .gym: return .HotelAmenities.gym
            case .spa: return .HotelAmenities.spa
            case .restaurant: return .HotelAmenities.restaurant
            case .bar: return .HotelAmenities.bar
            case .wifi: return .HotelAmenities.wifi
            case .parking: return .HotelAmenities.parking
            case .airConditioning: return .HotelAmenities.airConditioning
            case .roomService: return .HotelAmenities.roomService
            case .laundry: return .HotelAmenities.laundry
            case .concierge: return .HotelAmenities.concierge
            case .beachAccess: return .HotelAmenities.beachAccess
            case .skiAccess: return .HotelAmenities.skiAccess
            case .petFriendly: return .HotelAmenities.petFriendly
            case .smokingArea: return .HotelAmenities.smokingArea
            case .evCharging: return .HotelAmenities.evCharging
            case .businessCenter: return .HotelAmenities.businessCenter
            case .conferenceRoom: return .HotelAmenities.conferenceRoom
            case .childrenPlayground: return .HotelAmenities.childrenPlayground
            case .shuttle: return .HotelAmenities.shuttle
            case .breakfastIncluded: return .HotelAmenities.breakfastIncluded
        }
    }
    
    var isFeatured: Bool {
        switch self {
            case .pool, .wifi, .petFriendly, .breakfastIncluded, .parking:
                return true
                
            default:
                return false
        }
    }
    
    var icon: String {
        switch self {
            case .pool:
                return "figure.pool.swim"
                
            case .gym:
                return "dumbbell.fill"
                
            case .spa:
                return "apple.meditate"
                
            case .restaurant:
                return "fork.knife"
                
            case .bar:
                return "wineglass.fill"
                
            case .wifi:
                return "wifi"
                
            case .parking:
                return "parkingsign.circle.fill"
                
            case .airConditioning:
                return "air.conditioner.horizontal.fill"
                
            case .roomService:
                return "bell.fill"
                
            case .laundry:
                return "washer.fill"
                
            case .concierge:
                return "person.badge.key.fill"
                
            case .beachAccess:
                return "beach.umbrella.fill"
                
            case .skiAccess:
                return "figure.skiing.crosscountry"
                
            case .petFriendly:
                return "pawprint.fill"
                
            case .smokingArea:
                return "smoke.fill"
                
            case .evCharging:
                return "ev.plug.ac.type.1.fill"
                
            case .businessCenter:
                return "building.2.fill"
                
            case .conferenceRoom:
                return "mic.fill"
                
            case .childrenPlayground:
                return "figure.play"
                
            case .shuttle:
                return "bus.fill"
                
            case .breakfastIncluded:
                return "cup.and.saucer.fill"
        }
    }
}

struct Habitacion: Identifiable, Codable {
    var id: UUID
    var capacidad: Int
    var numero: Int
    var descripcion: String
    var imagenes: [String]
    var monto: Double
    var impuestos: Double
    var disponible: Bool
}

struct Hotel: Identifiable, Codable {
    var id: UUID
    var nombre: String
    var direccion: String
    var pais: String
    var estado: String
    var departamento: String
    var ciudad: String
    var descripcion: String
    var amenidades: [HotelAmenity]
    var estrellas: Int
    var ranking: Double
    var contactoCelular: String
    var contactoEmail: String
    var images: [String]
    var checkInHour: String
    var checkOutHour: String
    var valorMinimoModificacion: Double
    var habitaciones: [Habitacion]
}
