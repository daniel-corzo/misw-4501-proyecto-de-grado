//
//  FilterSortView.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 30/04/26.
//

import SwiftUI

// MARK: - Price Range Slider

struct PriceRangeSlider: View {
    @Binding var lowValue: Double
    @Binding var highValue: Double
    let bounds: ClosedRange<Double>
    let step: Double

    @State private var isDragging = false
    @State private var draggingLow = true

    private let thumbSize: CGFloat = 26

    var body: some View {
        GeometryReader { geometry in
            let trackWidth = geometry.size.width - thumbSize
            let lowFrac = CGFloat((lowValue - bounds.lowerBound) / (bounds.upperBound - bounds.lowerBound))
            let highFrac = CGFloat((highValue - bounds.lowerBound) / (bounds.upperBound - bounds.lowerBound))

            ZStack(alignment: .leading) {
                Capsule()
                    .fill(Color(.systemGray4))
                    .frame(height: 4)
                    .padding(.horizontal, thumbSize / 2)

                Rectangle()
                    .fill(Color.blue)
                    .frame(width: (highFrac - lowFrac) * trackWidth, height: 4)
                    .offset(x: thumbSize / 2 + lowFrac * trackWidth)

                Circle()
                    .fill(Color.blue)
                    .frame(width: thumbSize, height: thumbSize)
                    .shadow(color: .black.opacity(0.1), radius: 3, y: 1)
                    .offset(x: lowFrac * trackWidth)

                Circle()
                    .fill(Color.blue)
                    .frame(width: thumbSize, height: thumbSize)
                    .shadow(color: .black.opacity(0.1), radius: 3, y: 1)
                    .offset(x: highFrac * trackWidth)

                Color.clear
                    .contentShape(Rectangle())
                    .gesture(
                        DragGesture(minimumDistance: 0)
                            .onChanged { value in
                                let x = value.location.x - thumbSize / 2
                                let fraction = Double(min(max(x / trackWidth, 0), 1))
                                let raw = bounds.lowerBound + fraction * (bounds.upperBound - bounds.lowerBound)
                                let stepped = round(raw / step) * step

                                if !isDragging {
                                    isDragging = true
                                    draggingLow = abs(stepped - lowValue) <= abs(stepped - highValue)
                                }

                                if draggingLow {
                                    lowValue = min(max(stepped, bounds.lowerBound), highValue - step)
                                } else {
                                    highValue = max(min(stepped, bounds.upperBound), lowValue + step)
                                }
                            }
                            .onEnded { _ in
                                isDragging = false
                            }
                    )
            }
        }
        .frame(height: 30)
    }
}

// MARK: - Filter & Sort View

struct FilterSortView: View {
    var viewModel: ListHotelView.ViewModel
    var onApply: () -> Void

    @Environment(\.dismiss) private var dismiss

    @State private var sortOrder: HotelSortOrder
    @State private var priceLow: Double
    @State private var priceHigh: Double
    @State private var selectedStars: Set<Int>
    @State private var selectedAmenities: Set<HotelAmenity>

    private let featuredAmenities: [HotelAmenity] = [
        .wifi, .pool, .breakfastIncluded, .gym, .spa, .parking, .restaurant, .petFriendly
    ]

    init(viewModel: ListHotelView.ViewModel, onApply: @escaping () -> Void) {
        self.viewModel = viewModel
        self.onApply = onApply
        _sortOrder = State(initialValue: viewModel.sortOrder)
        _priceLow = State(initialValue: viewModel.priceLow)
        _priceHigh = State(initialValue: viewModel.priceHigh)
        _selectedStars = State(initialValue: viewModel.selectedStars)
        _selectedAmenities = State(initialValue: viewModel.selectedAmenities)
    }

    private func apply() {
        viewModel.sortOrder = sortOrder
        viewModel.priceLow = priceLow
        viewModel.priceHigh = priceHigh
        viewModel.selectedStars = selectedStars
        viewModel.selectedAmenities = selectedAmenities
        onApply()
        dismiss()
    }

    private typealias Defaults = ListHotelView.ViewModel

    private func formatPrice(_ value: Double) -> String {
        Int(value).formatted(.currency(code: "COP").precision(.fractionLength(0)))
    }

    private func reset() {
        sortOrder = Defaults.defaultSortOrder
        priceLow = Defaults.defaultPriceLow
        priceHigh = Defaults.defaultPriceHigh
        selectedStars = []
        selectedAmenities = []
    }

    var body: some View {
        VStack(spacing: 0) {
            // MARK: Header
            HStack {
                Button { dismiss() } label: {
                    Image(systemName: "xmark")
                        .font(.title3)
                        .foregroundStyle(.primary)
                }

                Spacer()

                Text(LocalizedStringResource.HotelList.filterAndSort)
                    .font(.headline)

                Spacer()

                Button(action: reset) {
                    Text(LocalizedStringResource.HotelList.reset)
                        .foregroundStyle(.blue)
                }
            }
            .padding()

            Divider()

            // MARK: Content
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    sortSection

                    Divider()

                    priceRangeSection

                    Divider()

                    starsSection

                    Divider()

                    amenitiesSection
                }
                .padding()
            }

            // MARK: Apply Button
            Button(action: apply) {
                Text(LocalizedStringResource.HotelList.showHotels)
                .fontWeight(.semibold)
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.blue)
                .clipShape(Capsule())
            }
            .padding()
        }
    }

    // MARK: - Sort Section

    private var sortSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(LocalizedStringResource.HotelList.sortBy)
                .font(.headline)

            ForEach(HotelSortOrder.allCases) { order in
                Button {
                    sortOrder = order
                } label: {
                    HStack {
                        Text(order.localizedName)
                            .foregroundStyle(.primary)

                        Spacer()

                        Image(systemName: sortOrder == order ? "circle.inset.filled" : "circle")
                            .foregroundStyle(sortOrder == order ? .blue : Color(.systemGray3))
                            .font(.title3)
                    }
                    .padding(.vertical, 4)
                }
            }
        }
    }

    // MARK: - Price Range Section

    private var priceRangeSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(LocalizedStringResource.HotelList.priceRange)
                    .font(.headline)

                Spacer()

                Text("\(formatPrice(priceLow)) - \(formatPrice(priceHigh))")
                    .foregroundStyle(.blue)
                    .fontWeight(.medium)
            }

            PriceRangeSlider(
                lowValue: $priceLow,
                highValue: $priceHigh,
                bounds: Defaults.defaultPriceLow...Defaults.defaultPriceHigh,
                step: 10_000
            )
            .padding(.vertical, 4)

            HStack {
                Text(formatPrice(Defaults.defaultPriceLow))
                    .font(.caption)
                    .foregroundStyle(.secondary)

                Spacer()

                Text("\(formatPrice(Defaults.defaultPriceHigh))+")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
    }

    // MARK: - Stars Section

    private var starsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(LocalizedStringResource.HotelList.stars)
                .font(.headline)

            HStack(spacing: 10) {
                starPill(label: String(localized: .HotelList.any), value: nil)

                ForEach([3, 4, 5], id: \.self) { star in
                    starPill(label: "\(star) \u{2606}", value: star)
                }
            }
        }
    }

    private func starPill(label: String, value: Int?) -> some View {
        let isSelected: Bool = if let value {
            selectedStars.contains(value)
        } else {
            selectedStars.isEmpty
        }

        return Button {
            if let value {
                if selectedStars.contains(value) {
                    selectedStars.remove(value)
                } else {
                    selectedStars.insert(value)
                }
            } else {
                selectedStars.removeAll()
            }
        } label: {
            Text(label)
                .font(.subheadline)
                .fontWeight(.medium)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(isSelected ? Color.blue.opacity(0.1) : Color(.systemGray6))
                .foregroundStyle(isSelected ? .blue : .primary)
                .clipShape(Capsule())
                .overlay(
                    Capsule()
                        .stroke(isSelected ? Color.blue : Color.clear, lineWidth: 1.5)
                )
        }
    }

    // MARK: - Amenities Section

    private var amenitiesSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(LocalizedStringResource.HotelList.popularAmenities)
                .font(.headline)

            ForEach(featuredAmenities, id: \.self) { amenity in
                Toggle(isOn: Binding(
                    get: { selectedAmenities.contains(amenity) },
                    set: { isOn in
                        if isOn {
                            selectedAmenities.insert(amenity)
                        } else {
                            selectedAmenities.remove(amenity)
                        }
                    }
                )) {
                    HStack {
                        Image(systemName: amenity.icon)
                            .frame(width: 24)
                            .foregroundStyle(.secondary)

                        Text(amenity.localizedName)
                    }
                }
            }
        }
    }
}
