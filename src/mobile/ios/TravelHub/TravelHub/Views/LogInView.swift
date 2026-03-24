//
//  LogInView.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 19/03/26.
//

import SwiftUI

struct LogInView: View {
    enum Field {
        case email, password
    }
    
    @FocusState private var focusedField: Field?
    @State private var viewModel = ViewModel()
    @State private var isHidingPassword: Bool = true
    @State private var showError = false
    @State private var isLoading = false
    
    @Binding var isLoggedIn: Bool
    
    var body: some View {
        ZStack {
            Color.formBackground
                .ignoresSafeArea()
            
            GeometryReader { geo in
                ScrollView(.vertical) {
                    VStack(spacing: 32) {
                        // MARK: - Icon + Welcome texts centrados
                        VStack(spacing: 8) {
                            Image(systemName: "bed.double.fill")
                                .resizable()
                                .scaledToFit()
                                .frame(width: 120, height: 120)
                                .foregroundStyle(.primary)
                            
                            Text(LocalizedStringResource.LogIn.title) // "Welcome Back"
                                .font(.title)
                                .bold()
                                .multilineTextAlignment(.center)
                            
                            Text(LocalizedStringResource.LogIn.description) // descripción
                                .foregroundStyle(.neutralDark)
                                .multilineTextAlignment(.center)
                        }
                        .frame(maxWidth: .infinity)
                        
                        // MARK: - Inputs
                        VStack(spacing: 24) {
                            
                            FormTextFieldView(
                                fieldName: .UserData.email,
                                icon: "envelope",
                                placeholder: LocalizedStringResource.LogIn.emailPlaceholder,
                                text: $viewModel.email
                            )
                            .keyboardType(.emailAddress)
                            .textContentType(.emailAddress)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled(true)
                            .focused($focusedField, equals: .email)
                            .submitLabel(.next)
                            .onSubmit { focusedField = .password }
                            
                            FormTextFieldView(
                                fieldName: .UserData.password,
                                icon: "lock",
                                placeholder: LocalizedStringResource.LogIn.passwordPlaceholder,
                                textInputAutocapitalization: .never,
                                isSecuredField: true,
                                text: $viewModel.password
                            )
                            .textContentType(.newPassword)
                            .focused($focusedField, equals: .password)
                            .submitLabel(.done)
                            .onSubmit { focusedField = nil }
                            
                            // Forgot Password button
                            HStack {
                                Spacer()
                                Button {
                                    // TODO: Acción para recuperar contraseña
                                } label: {
                                    Text(LocalizedStringResource.LogIn.forgotPassword)
                                        .font(.footnote)
                                        .foregroundStyle(.accent)
                                }
                            }
                        }
                        
                        // MARK: - Login button
                        Button {
                            isLoading = true
                            showError = false
                            
                            // 2️⃣ Simulación de login (API)
                            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                                isLoading = false
                                
                                if viewModel.email.isEmpty || viewModel.password.isEmpty {
                                    // ❌ Error: campos vacíos
                                    showError = true
                                } else {
                                    // ✅ Login OK: navegar
                                    isLoggedIn = true
                                }
                            }
                        } label: {
                            HStack {
                                    Spacer()
                                    
                                    if isLoading {
                                        ProgressView()
                                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                    } else {
                                        Text(LocalizedStringResource.LogIn.logInButton)
                                            .foregroundStyle(.white)
                                            .bold()
                                    }
                                    
                                    Spacer()
                                }
                        }
                        .padding(.vertical, 24)
                        .glassEffect(.regular.tint(.accent).interactive())
                        .clipShape(Capsule())
                        .shadow(color: .accent.opacity(0.2), radius: 15, y: 10)
                        .alert("Error", isPresented: $showError, actions: {
                            Button("OK", role: .cancel) { }
                        }, message: {
                            Text(LocalizedStringResource.LogIn.emailAndPasswordError)
                        })
                        
                        Divider()
                        
                        HStack {
                            Spacer()
                            Text(LocalizedStringResource.LogIn.dontHaveAnAccount)
                            
                            NavigationLink {
                                SignUpView()
                            } label: {
                                Text(LocalizedStringResource.LogIn.signUpText)
                                    .bold()
                                    .foregroundStyle(.accent)
                            }
                            
                            Spacer()
                        }
                        
                    }
                    .padding()
                    .frame(maxWidth: .infinity, minHeight: geo.size.height)
                }
                .scrollDismissesKeyboard(.immediately)
            }
        }
        .onTapGesture { focusedField = nil }
    }
}

#Preview {
    LogInView(isLoggedIn: .constant(false))
}
