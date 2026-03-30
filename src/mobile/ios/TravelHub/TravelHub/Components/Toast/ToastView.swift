//
//  ToastView.swift
//  TravelHub
//
//  Created by Andres Donoso on 29/03/26.
//

import SwiftUI

struct ToastView: View {
    let toast: Toast

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: toast.style.icon)
                .foregroundStyle(toast.style.color)
                .font(.system(size: 20))

            VStack(alignment: .leading) {
                if let title = toast.title {
                    Text(title)
                        .bold()
                        .foregroundStyle(toast.style.color)
                        .multilineTextAlignment(.leading)
                }
                
                Text(toast.message)
                    .font(.subheadline)
                    .multilineTextAlignment(.leading)
                    .foregroundStyle(toast.style.color)
            }

            Spacer()
        }
        .padding()
        .glassEffect(.clear.tint(toast.style.background))
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .shadow(
            color: toast.style.background.opacity(0.1),
            radius: 8,
            x: 0,
            y: 4
        )
        .padding(.horizontal)
        .padding(.top, 8)
    }
}

#Preview {
    ToastView(toast: .init(message: "Success toast", style: .success))
    ToastView(
        toast: .init(message: "Error toast", title: "Error", style: .error)
    )
    ToastView(toast: .init(message: "Info toast", style: .info))
    ToastView(toast: .init(message: "Warning toast", style: .warning))
}
