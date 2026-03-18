//
//  SignUpView.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/03/26.
//

import SwiftUI

struct SignUpView: View {
    @State private var fullName: String = ""
    
    var body: some View {
        ZStack {
            Color.formBackground
                .ignoresSafeArea()
            
            VStack(alignment: .leading) {
                Text(LocalizedStringResource.SignUp.title)
                    .font(.title)
                    .bold()
                
                Text(LocalizedStringResource.SignUp.description)
                    .foregroundStyle(.neutralDark)
                
                VStack {
                    VStack(alignment: .leading) {
                        Text(LocalizedStringResource.UserData.fullName)
                            .bold()
                        
                        CapsuleTextField(icon: "person", placeholder: "John Doe", textInputAutocapitalization: .words, text: $fullName)
                    }
                } //: VStack Form
            } //: VStack
        } //: ZStack Background
    }
}

#Preview {
    SignUpView()
}
