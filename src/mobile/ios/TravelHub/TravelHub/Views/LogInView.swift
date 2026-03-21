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
                            HStack {
                                Image(systemName: "envelope")
                                    .foregroundStyle(.neutral)
                                
                                TextField(LocalizedStringResource.LogIn.emailPlaceholder, text: $viewModel.email)
                                    .keyboardType(.emailAddress)
                                    .textContentType(.emailAddress)
                                    .textInputAutocapitalization(.never)
                                    .autocorrectionDisabled(true)
                                    .focused($focusedField, equals: .email)
                                    .submitLabel(.next)
                                    .onSubmit { focusedField = .password }
                            }
                            .padding()
                            .background(Color.white)
                            .clipShape(Capsule())
                            .overlay(Capsule().stroke(Color.gray.opacity(0.4), lineWidth: 1))
                            
                            // Password con "ojito"
                            HStack {
                                Image(systemName: "lock")
                                    .foregroundStyle(.neutral)
                                
                                Group {
                                    if isHidingPassword {
                                        SecureField(LocalizedStringResource.LogIn.passwordPlaceholder, text: $viewModel.password)
                                    } else {
                                        TextField(LocalizedStringResource.LogIn.passwordPlaceholder, text: $viewModel.password)
                                            .textInputAutocapitalization(.never)
                                    }
                                }
                                .textContentType(.newPassword)
                                .focused($focusedField, equals: .password)
                                .submitLabel(.done)
                                .onSubmit { focusedField = nil }
                                
                                // Botón del ojo
                                Image(systemName: isHidingPassword ? "eye" : "eye.slash")
                                    .foregroundStyle(.neutral)
                                    .onTapGesture { isHidingPassword.toggle() }
                            }
                            .padding()
                            .background(Color.white)
                            .clipShape(Capsule())
                            .overlay(Capsule().stroke(Color.gray.opacity(0.4), lineWidth: 1))
                            
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
                            // TODO: Implement login
                        } label: {
                            HStack {
                                Spacer()
                                Text(LocalizedStringResource.LogIn.logInButton)
                                    .foregroundStyle(.white)
                                    .bold()
                                Image(systemName: "arrow.right")
                                    .foregroundStyle(.white)
                                    .bold()
                                Spacer()
                            }
                        }
                        .padding(.vertical, 24)
                        .glassEffect(.regular.tint(.accent).interactive())
                        .clipShape(Capsule())
                        .shadow(color: .accent.opacity(0.2), radius: 15, y: 10)
                        
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
                    // 🔹 CAMBIO: usamos GeometryReader para altura
                    .frame(maxWidth: .infinity, minHeight: geo.size.height)
                }
                .scrollDismissesKeyboard(.immediately)
            }
        }
        .onTapGesture { focusedField = nil }
    }
}

#Preview {
    LogInView()
}
