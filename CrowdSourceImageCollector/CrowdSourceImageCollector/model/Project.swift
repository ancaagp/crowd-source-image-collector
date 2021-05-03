//
//  Project.swift
//  CrowdSourceImageCollector
//
//  Created by Jonatas Chagas on 22.4.2021.
//

import SwiftUI

struct Project: Codable, Identifiable {
    var id: Int
    var name: String
    var description: String
    var labels: String
    
    static let example = Project(id: 1, name: "Dog Pictures", description: "10 most popular breeds", labels: "German Shepherd,Bulldog,Pitbull,Poodle")
    
}

class ProjectModel : ObservableObject {
    
    @Published var projects = [Project]()
    
    func parse(jsonData: Data) {
        do {
            print("Data: " + String(decoding: jsonData, as: UTF8.self));
            
            projects = try JSONDecoder().decode([Project].self,
                                                from: jsonData);
        } catch DecodingError.keyNotFound(let key, let context) {
            Swift.print("could not find key \(key) in JSON: \(context.debugDescription)")
        } catch DecodingError.valueNotFound(let type, let context) {
            Swift.print("could not find type \(type) in JSON: \(context.debugDescription)")
        } catch DecodingError.typeMismatch(let type, let context) {
            Swift.print("type mismatch for type \(type) in JSON: \(context.debugDescription)")
        } catch DecodingError.dataCorrupted(let context) {
            Swift.print("data found to be corrupted in JSON: \(context.debugDescription)")
        } catch let error as NSError {
            NSLog("Error in read(from:ofType:) domain= \(error.domain), description= \(error.localizedDescription)")
        }
    }
    
    func loadJson(fromURLString urlString: String,
                          completion: @escaping (Result<Data, Error>) -> Void) {
        if let url = URL(string: urlString) {
            let urlSession = URLSession(configuration: .default).dataTask(with: url) { (data, response, error) in
                if let error = error {
                    completion(.failure(error))
                }
                
                if let data = data {
                    completion(.success(data))
                }
            }
            
            urlSession.resume()
        }
    }
    
    func loadProjects(completion: @escaping (Result<[Project], Error>) -> Void) {
        projects.removeAll();
        let urlString = Constants.API_ENDPOINT + "/api/projects"
        self.loadJson(fromURLString: urlString) { (result) in
            switch result {
            case .success(let data):
                self.parse(jsonData: data)
                completion(.success(self.projects))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
}
