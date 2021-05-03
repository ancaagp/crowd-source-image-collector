//
//  CameraView.swift
//  CrowdSourceImageCollector
//
//  Created by Jonatas Chagas on 24.4.2021.
//

import SwiftUI

class ImageModel: ObservableObject {
    var projectId = ""
    var label = ""
    var description = ""
}

struct CameraView: View {
    
    @ObservedObject var labeledImageModel: LabeledImageModel = LabeledImageModel()
    
    @State var project: Project = Project.example
    
    @State var image: Image?
    @State var inputImage: UIImage? = nil
    @State var showCaptureImageView: Bool = false
    @State var labelImage: String = ""
    
    @StateObject var model = ImageModel()
    
    func loadImage() {
        guard let inputImage = inputImage else { return }
        image = Image(uiImage: inputImage)
    }
    
    var body: some View {
        switch labeledImageModel.state {
            case .uploading:
                ProgressView()
            default:
                Form {
                    Section {
                        ZStack {
                            VStack {
                                
                                if let image = image {
                                    image
                                        .resizable()
                                        .scaledToFit()
                                } else {
                                    Text("Tap to select a picture")
                                        .foregroundColor(.black)
                                        .font(.headline)
                                }
                            }
                            .sheet(isPresented: $showCaptureImageView, onDismiss: loadImage) {
                                CaptureImageView(image: self.$inputImage)
                            }
                            .onTapGesture {
                                self.showCaptureImageView.toggle()
                            }
                        }
                    }
                    
                    Section {
                        Picker("Label", selection: $labelImage) {
                            ForEach(self.project.labels.components(separatedBy: ","), id: \.self) {
                                Text($0)
                            }
                        }
                        
                        TextField("Description", text: $model.description)
                        
                        Button("Submit") {
                            let pjId = project.id
                            let lab = self.labelImage
                            let desc = self.model.description
                            self.labeledImageModel.uploadImage(projectId: pjId, label: lab, description: desc, uiImage: self.inputImage)
                        }
                    }
                }
                .alert(isPresented: $labeledImageModel.showAlert ) {
                    switch labeledImageModel.state {
                    case .parametersNotSelected:
                        return Alert(title: Text("Error"), message: Text("Please select an image, label and fill a proper description. "), dismissButton: .default(Text("Got it!")) {
                            self.labeledImageModel.state = LabeledImageModel.State.idle
                        });
                    
                    case .failed:
                        return Alert(title: Text("Error"), message: Text("Error uploading the image. Check your internet connection and try again."), dismissButton: .default(Text("Ok")) {
                            self.labeledImageModel.state = LabeledImageModel.State.idle
                        });
                    default:
                        return Alert(title: Text("Success"), message: Text("Image uploaded to the server. Thank you!"), dismissButton: .default(Text("Ok")) {
                            self.labeledImageModel.state = LabeledImageModel.State.idle
                        });
                    }
                }
        }
    }
}

struct CameraView_Previews: PreviewProvider {
    static var previews: some View {
        CameraView(project: Project.example)
    }
}
