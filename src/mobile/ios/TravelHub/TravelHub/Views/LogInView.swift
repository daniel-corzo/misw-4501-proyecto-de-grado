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
    
    @Environment(\.authService) private var authService: AuthService
    @Environment(\.userService) private var userService: UserService
    @Environment(\.toastManager) private var toastManager: ToastManager
    
    @FocusState private var focusedField: Field?
    @State private var viewModel = ViewModel()
    @State private var isHidingPassword: Bool = true
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
                            .textContentType(.password)
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
                            Task {
                                focusedField = nil
                                isLoading = true
                                
                                do {
                                    let _ = try await viewModel.logIn()
                                    let me = try await userService.getMe()
                                    if me.tipo == TipoUsuario.viajero.rawValue {
                                        isLoggedIn = true
                                    } else {
                                        toastManager.warning("No se puede acceder a la aplicación con este tipo de usuario")
                                    }
                                } catch {
                                    toastManager.error(error.localizedDescription, title: "Error")
                                }
                                isLoading = false
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
                        .disabled(!viewModel.canSubmit || isLoading)
                        .opacity((!viewModel.canSubmit || isLoading) ? 0.6 : 1.0)
                        
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
        .task {
            self.viewModel.authService = self.authService
        }
    }
}

#Preview {
    LogInView(isLoggedIn: .constant(false))
        // TODO: Change injected service for a mock
        .environment(\.authService, AuthServiceImpl(httpService: HttpServiceImpl.shared))
}
