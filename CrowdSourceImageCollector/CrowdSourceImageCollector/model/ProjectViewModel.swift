//
//  ProjectViewModel.swift
//  CrowdSourceImageCollector
//
//  Created by Jonatas Chagas on 23.4.2021.
//

import SwiftUI

class ProjectViewModel: ObservableObject {
    
    enum State {
        case idle
        case loading
        case failed(Error)
        case loaded([Project])
    }
    
    @Published private(set) var state = State.idle
        
    private let loader: ProjectModel

    init(loader: ProjectModel) {
        self.loader = loader
    }

    func load() {
        state = .loading
        loader.loadProjects() { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let projects):
                    self?.state = .loaded(projects)
                case .failure(let error):
                    self?.state = .failed(error)
                }
            }
        }
    }

}
