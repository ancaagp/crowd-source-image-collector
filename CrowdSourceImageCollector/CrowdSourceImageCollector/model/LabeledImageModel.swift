//
//  LabeledImage.swift
//  CrowdSourceImageCollector
//
//  Created by Jonatas Chagas on 25.4.2021.
//

import SwiftUI
import Alamofire

class LabeledImageModel : ObservableObject
{
    let IMAGE_API_ENDPOINT = Constants.API_ENDPOINT + "/api/images/"
    
    enum State {
        case idle
        case parametersNotSelected
        case uploading
        case failed
        case success
    }
    
    @Published var state = State.idle
    @Published var showAlert = false;
    
    func uploadImage(projectId: Int, label: String, description: String, uiImage: UIImage?) {
        
        if (label.isEmpty || projectId == -1 || description.isEmpty || uiImage == nil) {
            self.state = .parametersNotSelected
            self.showAlert = true;
            return;
        }
        
        let pngImage = uiImage!.pngData()
        
        AF.upload(multipartFormData: { multipartFormData in
            multipartFormData.append(pngImage!, withName: "image", fileName: label + ".png", mimeType: "image/png")
            multipartFormData.append(Data(String(projectId).utf8), withName: "project")
            multipartFormData.append(Data(label.utf8), withName: "label")
            multipartFormData.append(Data(description.utf8), withName: "description")
        }, to:  Constants.API_ENDPOINT + "/api/images")
        .uploadProgress {_ in
            self.state = .uploading
        }
        .response { response in
            switch response.result {
                case .success:
                    self.state = .success;
                    self.showAlert = true;
                case .failure:
                    self.state = .failed;
                    self.showAlert = true;
            }
        }
    }
    
}
