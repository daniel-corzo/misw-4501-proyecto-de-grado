//
//  DateRange.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/04/26.
//

import Foundation

struct DateRange {
    var start: Date
    var end: Date

    var nights: Int {
        Calendar.current.dateComponents([.day], from: start, to: end).day ?? 0
    }
}
