import { app } from "../../../scripts/app.js";
import { addCssLink } from "./utils/dom.js";
import { HuggingFaceDownloaderUI } from "./ui/UI.js";

console.log("Loading HuggingFace UI...");

// --- Configuration ---
const EXTENSION_NAME = "HuggingFace";
const CSS_URL = `../huggingfaceDownloader.css`;
const PLACEHOLDER_IMAGE_URL = `/extensions/ComfyUI-HuggingFace/images/placeholder.jpg`;

// Add Menu Button to ComfyUI
function addMenuButton() {
    const buttonGroup = document.querySelector(".comfyui-button-group");

    if (!buttonGroup) {
        console.warn(`[${EXTENSION_NAME}] ComfyUI button group not found. Retrying...`);
        setTimeout(addMenuButton, 500);
        return;
    }

    if (document.getElementById("huggingface-downloader-button")) {
        console.log(`[${EXTENSION_NAME}] Button already exists.`);
        return;
    }

    const huggingfaceButton = document.createElement("button");
    huggingfaceButton.innerHTML = "🤗 HuggingFace";
    huggingfaceButton.id = "huggingface-downloader-button";
    huggingfaceButton.title = "Open HuggingFace Model Downloader";

    huggingfaceButton.onclick = async () => {
        if (!window.huggingfaceDownloaderUI) {
            console.info(`[${EXTENSION_NAME}] Creating HuggingFaceDownloaderUI instance...`);
            window.huggingfaceDownloaderUI = new HuggingFaceDownloaderUI();
            document.body.appendChild(window.huggingfaceDownloaderUI.modal);

            try {
                await window.huggingfaceDownloaderUI.initializeUI();
                console.info(`[${EXTENSION_NAME}] UI Initialization complete.`);
            } catch (error) {
                console.error(`[${EXTENSION_NAME}] Error during UI initialization:`, error);
                window.huggingfaceDownloaderUI?.showToast("Error initializing UI components. Check console.", "error", 5000);
            }
        }

        if (window.huggingfaceDownloaderUI) {
            window.huggingfaceDownloaderUI.openModal();
        } else {
            console.error(`[${EXTENSION_NAME}] Cannot open modal: UI instance not available.`);
            alert("HuggingFace failed to initialize. Please check the browser console for errors.");
        }
    };

    buttonGroup.appendChild(huggingfaceButton);
    console.log(`[${EXTENSION_NAME}] HuggingFace button added to .comfyui-button-group.`);

    const menu = document.querySelector(".comfy-menu");
    if (!buttonGroup.contains(huggingfaceButton) && menu && !menu.contains(huggingfaceButton)) {
        console.warn(`[${EXTENSION_NAME}] Failed to append button to group, falling back to menu.`);
        const settingsButton = menu.querySelector("#comfy-settings-button");
        if (settingsButton) {
            settingsButton.insertAdjacentElement("beforebegin", huggingfaceButton);
        } else {
            menu.appendChild(huggingfaceButton);
        }
    }
}

// --- Initialization ---
app.registerExtension({
    name: "ComfyUI-HuggingFace.HuggingFaceDownloader",
    async setup(appInstance) {
        console.log(`[${EXTENSION_NAME}] Setting up HuggingFace Extension...`);
        addCssLink(CSS_URL);
        addMenuButton();

        // Optional: Pre-check placeholder image
        fetch(PLACEHOLDER_IMAGE_URL)
            .then(res => {
                if (!res.ok) {
                    console.warn(`[${EXTENSION_NAME}] Placeholder image not found at ${PLACEHOLDER_IMAGE_URL}.`);
                }
            })
            .catch(err => console.warn(`[${EXTENSION_NAME}] Error checking for placeholder image:`, err));

        console.log(`[${EXTENSION_NAME}] Extension setup complete. UI will initialize on first click.`);
    },
});
