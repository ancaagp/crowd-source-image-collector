//
//  ProjectView.swift
//  CrowdSourceImageCollector
//
//  Created by Jonatas Chagas on 22.4.2021.
//

import SwiftUI

struct ProjectView: View {
    
    @ObservedObject var viewModel: ProjectViewModel
    
    var body: some View {
        switch viewModel.state {
            case .idle:
                // Render a clear color and start the loading process
                // when the view first appears, which should make the
                // view model transition into its loading state:
                Color.clear.onAppear(perform: viewModel.load)
            case .loading:
                ProgressView()
            case .failed(_):
                VStack {
                    Text("Error fetching the projects.")
                    Button("Try Again") {
                        viewModel.load();
                    }
                }
            case .loaded(let projects):
                NavigationView {
                    List {
                        Section(header: Text("Projects")) {
                            ForEach(projects) { project in
                                HStack {
                                    NavigationLink(destination: CameraView(project: project)) {
                                        Text(project.name)
                                        Spacer()
                                        Text(project.description)
                                    }
                                }
                            }
                        }
                        Button("Refresh") {
                            viewModel.load()
                        }
                    }
                }
            }
    }
}

struct ProjectView_Previews: PreviewProvider {
    static var previews: some View {
        ProjectView(viewModel: ProjectViewModel(loader: ProjectModel()))
    }
}
