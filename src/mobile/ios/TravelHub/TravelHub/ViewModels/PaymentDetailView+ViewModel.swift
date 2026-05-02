//
//  PaymentDetailView+ViewModel.swift
//  TravelHub
//
//  Created by Andres Donoso on 2/05/26.
//

import Foundation

extension PaymentDetailView {
    @Observable
    class ViewModel {
        var paymentService: PaymentService = PaymentServiceKey.defaultValue
        var toastManager: ToastManager = ToastManagerKey.defaultValue
        
        var isLoading = false

        @MainActor
        func pay(
            monto: Int,
            medioDePago: String,
            creditCardNumber: String,
            cardholderName: String,
            cvv: String,
            expirationDate: String
        ) async {
            isLoading = true
            defer { isLoading = false }
            
            do {
                let _ = try await self.paymentService.pay(
                    paymentInfo: NewPayment(
                        monto: monto,
                        medioDePago: medioDePago,
                        creditCardNumber: creditCardNumber,
                        cardholderName: cardholderName,
                        cvv: cvv,
                        expirationDate: expirationDate
                    )
                )
                
                self.toastManager.success(String(localized: .Payment.paymentSuccessfulDescription), title: String(localized: .Payment.paymentSuccessfulTitle))
            } catch {
                self.toastManager.error(error.localizedDescription)
            }
        }
    }
}
