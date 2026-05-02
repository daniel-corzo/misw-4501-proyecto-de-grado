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
            expirationDate: String,
            showSuccessToast: Bool = true
        ) async -> Payment? {
            isLoading = true
            defer { isLoading = false }

            do {
                let payment = try await self.paymentService.pay(
                    paymentInfo: NewPayment(
                        monto: monto,
                        medioDePago: medioDePago,
                        creditCardNumber: creditCardNumber,
                        cardholderName: cardholderName,
                        cvv: cvv,
                        expirationDate: expirationDate
                    )
                )

                if showSuccessToast {
                    self.toastManager.success(
                        String(localized: .Payment.paymentSuccessfulDescription),
                        title: String(localized: .Payment.paymentSuccessfulTitle)
                    )
                }

                return payment
            } catch is CancellationError {
                return nil
            } catch {
                self.toastManager.error(error.localizedDescription)
                return nil
            }
        }
        
        func expirationDateIsValid(_ expirationDate: String) -> Bool {
            let dateParts = expirationDate.split(separator: "/")
            print(dateParts)
            var month: Int, year: Int
            
            if dateParts.count == 1 {
                month = Int(dateParts[0])!
                
                if month > 12 || month == 0 {
                    return false
                }
            }
            
            if dateParts.count == 2 {
                month = Int(dateParts[0])!
                year = Int(dateParts[1])!
                let today = Date()
                let currentYear = Calendar.current.component(.year, from: today) % 100
                let currentMonth = Calendar.current.component(.month, from: today)
                
                if year < currentYear {
                    return false
                } else if year == currentYear && month < currentMonth {
                    return false
                }
            }
            
            return true
        }
    }
}
