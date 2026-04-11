//
//  AppConfig.swift
//  TravelHub
//
//  Created by Andres Donoso on 29/03/26.
//

import Foundation

enum AppConfig {
    static var baseURL: URL {
        guard let urlString = Bundle.main.object(forInfoDictionaryKey: "BASE_URL") as? String,
              let url = URL(string: urlString) else {
            fatalError("BASE_URL not set in Info.plist")
        }
        
        return url
    }
}
