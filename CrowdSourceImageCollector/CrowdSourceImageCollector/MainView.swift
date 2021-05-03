//
//  MainView.swift
//  CrowdSourceImageCollector
//
//  Created by Jonatas Chagas on 22.4.2021.
//

import SwiftUI

struct MainView: View {
    var body: some View {
        TabView {
            ProjectView(viewModel: ProjectViewModel(loader: ProjectModel()))
                .tabItem { Label("Tasks", systemImage: "camera") }
            SummaryView()
                .tabItem { Label("My Account", systemImage: "person.crop.circle") }
        }
    }
}

struct MainView_Previews: PreviewProvider {
    static var previews: some View {
        MainView()
    }
}
