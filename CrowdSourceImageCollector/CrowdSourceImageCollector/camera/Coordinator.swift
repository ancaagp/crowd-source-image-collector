import SwiftUI

class Coordinator: NSObject, UINavigationControllerDelegate,
                   UIImagePickerControllerDelegate {
    
    let parent: CaptureImageView

    init(_ parent: CaptureImageView) {
        self.parent = parent
    }
    
    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
        if let uiImage = info[.originalImage] as? UIImage {
            parent.image = uiImage
        }

        parent.presentationMode.wrappedValue.dismiss()
    }
}
