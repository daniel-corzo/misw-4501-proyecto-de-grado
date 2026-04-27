//
//  DateRangePickerView.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/04/26.
//

import SwiftUI

struct DateRangePickerView: View {

    @Binding var dateRange: DateRange

    @State private var currentMonth: Date = .now
    @State private var selecting: SelectionStep = .start

    private enum SelectionStep { case start, end }

    private let columns = Array(
        repeating: GridItem(.flexible(), spacing: 0),
        count: 7
    )

    private var calendar: Calendar {
        Calendar.current
    }
    private var weekDaySymbols: [String] {
        let symbols = calendar.shortStandaloneWeekdaySymbols
        let firstWeekdayIndex = calendar.firstWeekday - 1
        let rotatedSymbols =
            Array(symbols[firstWeekdayIndex...])
            + Array(symbols[..<firstWeekdayIndex])
        return rotatedSymbols.map {
            String($0.prefix(1)).uppercased()
        }
    }
    private var daysInMonth: [Date?] {
        guard
            let monthStart = calendar.date(
                from: calendar.dateComponents(
                    [.year, .month],
                    from: currentMonth
                )
            ),
            let range = calendar.range(
                of: .day,
                in: .month,
                for: monthStart
            )
        else { return [] }
        let weekday = calendar.component(.weekday, from: monthStart)
        let leadingEmptyCount = (weekday - calendar.firstWeekday + 7) % 7
        let leadingEmpties: [Date?] = Array(
            repeating: nil,
            count: leadingEmptyCount
        )
        let days: [Date?] = range.compactMap {
            calendar.date(byAdding: .day, value: $0 - 1, to: monthStart)
        }
        return leadingEmpties + days
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {

            Text(LocalizedStringResource.Dates.selectDates)
                .font(.title3)
                .fontWeight(.bold)

            HStack {
                Button {
                    withAnimation(.easeInOut(duration: 0.3)) {
                        currentMonth =
                            Calendar.current.date(
                                byAdding: .month,
                                value: -1,
                                to: currentMonth
                            ) ?? currentMonth
                    }
                } label: {
                    Image(systemName: "chevron.left")
                        .foregroundStyle(.primary)
                }

                Spacer()

                Text(currentMonth.formatted(.dateTime.month(.wide).year()))
                    .font(.headline)
                    .contentTransition(.numericText())
                    .animation(.easeInOut(duration: 0.3), value: currentMonth)

                Spacer()

                Button {
                    withAnimation(.easeInOut(duration: 0.3)) {
                        currentMonth =
                            Calendar.current.date(
                                byAdding: .month,
                                value: 1,
                                to: currentMonth
                            ) ?? currentMonth
                    }
                } label: {
                    Image(systemName: "chevron.right")
                        .foregroundStyle(.primary)
                }
            }

            LazyVGrid(columns: columns, spacing: 0) {
                ForEach(Array(weekDaySymbols.enumerated()), id: \.offset) {
                    _,
                    symbol in
                    Text(symbol)
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundStyle(.secondary)
                        .frame(maxWidth: .infinity)
                        .padding(.bottom, 8)
                }

                ForEach(Array(daysInMonth.enumerated()), id: \.offset) {
                    index,
                    date in
                    if let date {
                        DayCell(
                            date: date,
                            dateRange: dateRange,
                            columnIndex: index % 7,
                            onTap: { handleTap(date) }
                        )
                    } else {
                        Color.clear
                            .frame(height: 40)
                    }
                }
            }
            .transition(
                .asymmetric(
                    insertion: .move(edge: .trailing).combined(with: .opacity),
                    removal: .move(edge: .leading).combined(with: .opacity)
                )
            )
            .animation(.easeInOut(duration: 0.3), value: currentMonth)
        }
    }

    private func handleTap(_ date: Date) {
        switch selecting {
        case .start:
            withAnimation(.spring(response: 0.35, dampingFraction: 0.7)) {
                dateRange = DateRange(start: date, end: date)
            }
            selecting = .end
        case .end:
            if date < dateRange.start {
                withAnimation(.spring(response: 0.35, dampingFraction: 0.7)) {
                    dateRange = DateRange(start: date, end: date)
                }
            } else {
                withAnimation(.spring(response: 0.35, dampingFraction: 0.7)) {
                    dateRange.end = date
                }
                selecting = .start
            }
        }
    }
}

private struct DayCell: View {

    let date: Date
    let dateRange: DateRange
    let columnIndex: Int
    let onTap: () -> Void

    @State private var isPressed = false

    private var day: Int { Calendar.current.component(.day, from: date) }
    private var isStart: Bool {
        Calendar.current.isDate(date, inSameDayAs: dateRange.start)
    }
    private var isEnd: Bool {
        Calendar.current.isDate(date, inSameDayAs: dateRange.end)
    }
    private var isInRange: Bool {
        date > dateRange.start && date < dateRange.end
    }
    private var isSingleDay: Bool {
        Calendar.current.isDate(dateRange.start, inSameDayAs: dateRange.end)
    }
    private var isFirstColumn: Bool { columnIndex == 0 }
    private var isLastColumn: Bool { columnIndex == 6 }
    private var isPast: Bool {
        Calendar.current.compare(date, to: .now, toGranularity: .day)
            != .orderedDescending
    }

    var body: some View {
        Text("\(day)")
            .font(.subheadline)
            .fontWeight(isStart || isEnd ? .bold : .regular)
            .foregroundStyle(
                isPast
                    ? Color(.systemGray4)
                    : isStart || isEnd ? .white : isInRange ? .accent : .primary
            )
            .frame(maxWidth: .infinity)
            .frame(height: 40)
            .background { rangeBackground }
            .scaleEffect(isPressed ? 0.88 : 1.0)
            .animation(
                .spring(response: 0.25, dampingFraction: 0.6),
                value: isPressed
            )
            .onTapGesture {
                guard !isPast else { return }
                isPressed = true
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.12) {
                    isPressed = false
                }
                onTap()
            }
    }

    @ViewBuilder
    private var rangeBackground: some View {
        if isSingleDay && isStart {
            Circle()
                .fill(Color.accentColor)
                .padding(.horizontal, 4)

        } else if isStart {
            HStack(spacing: 0) {
                Color.clear
                Color.accentColor.opacity(0.15)
            }
            .overlay(
                RoundedRectangle(cornerRadius: 50)
                    .fill(.accent),
                alignment: .center
            )

        } else if isEnd {
            HStack(spacing: 0) {
                Color.accentColor.opacity(0.15)
                Color.clear
            }
            .overlay(
                RoundedRectangle(cornerRadius: 50)
                    .fill(.accent),
                alignment: .center
            )

        } else if isInRange {
            Color.accentColor.opacity(0.15)
                .transition(.scale.combined(with: .opacity))
        }
    }
}

private func makeDate(_ string: String) -> Date {
    let formatter = ISO8601DateFormatter()
    formatter.formatOptions = [.withFullDate]
    formatter.timeZone = .current
    return formatter.date(from: string)!
}

#Preview {
    @Previewable @State var dateRange = DateRange(
        start: makeDate("2026-04-26"),
        end: makeDate("2026-04-30")
    )
    
    DateRangePickerView(dateRange: $dateRange)
        .padding()
}
