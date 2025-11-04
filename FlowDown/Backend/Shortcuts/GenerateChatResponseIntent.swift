import AppIntents
import ChatClientKit
import Foundation
import UIKit
import UniformTypeIdentifiers

struct GenerateChatResponseIntent: AppIntent {
    static var title: LocalizedStringResource {
        LocalizedStringResource("Quick Reply", defaultValue: "Quick Reply")
    }

    static var description = IntentDescription(
        LocalizedStringResource(
            "Send a message and get the model's response.",
            defaultValue: "Send a message and get the model's response."
        )
    )

    @Parameter(
        title: LocalizedStringResource("Model", defaultValue: "Model"),
        requestValueDialog: IntentDialog("Which model should answer?")
    )
    var model: ShortcutsEntities.ModelEntity?

    @Parameter(
        title: LocalizedStringResource("Message", defaultValue: "Message"),
        requestValueDialog: IntentDialog("What do you want to ask?")
    )
    var message: String

    static var parameterSummary: some ParameterSummary {
        Summary("Quick Reply")
    }

    func perform() async throws -> some IntentResult & ReturnsValue<String> & ProvidesDialog {
        let response = try await InferenceIntentHandler.execute(
            model: model,
            message: message,
            image: nil,
            options: .init(allowsImages: false)
        )
        let dialog = IntentDialog(.init(stringLiteral: response))
        return .result(value: response, dialog: dialog)
    }
}

@available(iOS 18.0, macCatalyst 18.0, *)
struct GenerateChatResponseWithImagesIntent: AppIntent {
    static var title: LocalizedStringResource {
        LocalizedStringResource("Quick Reply with Image", defaultValue: "Quick Reply with Image")
    }

    static var description = IntentDescription(
        LocalizedStringResource(
            "Send a message with an image and get the model's response.",
            defaultValue: "Send a message with an image and get the model's response."
        )
    )

    @Parameter(
        title: LocalizedStringResource("Model", defaultValue: "Model"),
        requestValueDialog: IntentDialog("Which model should answer?")
    )
    var model: ShortcutsEntities.ModelEntity?

    @Parameter(
        title: LocalizedStringResource("Message", defaultValue: "Message"),
        requestValueDialog: IntentDialog("What do you want to ask?")
    )
    var message: String

    @Parameter(
        title: LocalizedStringResource("Image", defaultValue: "Image"),
        supportedContentTypes: [.image],
        requestValueDialog: IntentDialog("Select an image to include.")
    )
    var image: IntentFile?

    static var parameterSummary: some ParameterSummary {
        Summary("Quick Reply with Image")
    }

    func perform() async throws -> some IntentResult & ReturnsValue<String> & ProvidesDialog {
        let response = try await InferenceIntentHandler.execute(
            model: model,
            message: message,
            image: image,
            options: .init(allowsImages: true)
        )
        let dialog = IntentDialog(.init(stringLiteral: response))
        return .result(value: response, dialog: dialog)
    }
}
