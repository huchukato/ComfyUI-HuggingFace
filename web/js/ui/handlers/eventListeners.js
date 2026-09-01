import { HuggingFaceDownloaderAPI } from "../../api/huggingface.js";
export function setupEventListeners(ui) {
    // Modal close
    ui.closeButton.addEventListener('click', () => ui.closeModal());
    ui.modal.addEventListener('click', (event) => {
        if (event.target === ui.modal) ui.closeModal();
    });

    // Tab switching
    ui.tabContainer.addEventListener('click', (event) => {
        if (event.target.matches('.huggingface-downloader-tab')) {
            ui.switchTab(event.target.dataset.tab);
        }
    });

    // --- FORMS ---
    ui.downloadForm.addEventListener('submit', (event) => {
        event.preventDefault();
        ui.handleDownloadSubmit();
    });

    // Change of model type should refresh subdir list
    ui.downloadModelTypeSelect.addEventListener('change', async () => {
        await ui.loadAndPopulateSubdirs(ui.downloadModelTypeSelect.value);
    });

    // Create new model type folder (first-level under models/)
    ui.createModelTypeButton.addEventListener('click', async () => {
        const name = prompt('Enter new model type folder name (will be created under models/)');
        if (!name) return;
        try {
            const res = await HuggingFaceDownloaderAPI.createModelType(name);
            if (res && res.success) {
                await ui.populateModelTypes();
                ui.downloadModelTypeSelect.value = res.name;
                await ui.loadAndPopulateSubdirs(res.name);
                ui.showToast(`Created model type folder: ${res.name}`, 'success');
            } else {
                ui.showToast(res?.error || 'Failed to create model type folder', 'error');
            }
        } catch (e) {
            ui.showToast(e.details || e.message || 'Error creating model type folder', 'error');
        }
    });

    // Create new subfolder under current model type
    ui.createSubdirButton.addEventListener('click', async () => {
        const type = ui.downloadModelTypeSelect.value;
        const name = prompt('Enter new subfolder name (you can include nested paths like A/B):');
        if (!name) return;
        try {
            const res = await HuggingFaceDownloaderAPI.createModelDir(type, name);
            if (res && res.success) {
                await ui.loadAndPopulateSubdirs(type);
                if (ui.subdirSelect) ui.subdirSelect.value = res.created || '';
                ui.showToast(`Created folder: ${res.created}`, 'success');
            } else {
                ui.showToast(res?.error || 'Failed to create folder', 'error');
            }
        } catch (e) {
            ui.showToast(e.details || e.message || 'Error creating folder', 'error');
        }
    });

    ui.searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        if (!ui.searchQueryInput.value.trim() && ui.searchTypeSelect.value === 'any' && ui.searchBaseModelSelect.value === 'any') {
            ui.showToast("Please enter a search query or select a filter.", "error");
            if (ui.searchResultsContainer) ui.searchResultsContainer.innerHTML = '<p>Please enter a search query or select a filter.</p>';
            if (ui.searchPaginationContainer) ui.searchPaginationContainer.innerHTML = '';
            return;
        }
        ui.searchPagination.currentPage = 1;
        ui.handleSearchSubmit();
    });

    ui.settingsForm.addEventListener('submit', (event) => {
        event.preventDefault();
        ui.handleSettingsSave();
    });
    if (ui.settingsSetGlobalRootButton) {
        ui.settingsSetGlobalRootButton.addEventListener('click', () => {
            ui.handleSetGlobalRoot();
        });
    }
    if (ui.settingsClearGlobalRootButton) {
        ui.settingsClearGlobalRootButton.addEventListener('click', () => {
            ui.handleClearGlobalRoot();
        });
    }

    // Download form inputs
    ui.modelUrlInput.addEventListener('input', () => ui.debounceFetchDownloadPreview());
    ui.modelUrlInput.addEventListener('paste', () => ui.debounceFetchDownloadPreview(0));
    ui.modelVersionIdInput.addEventListener('blur', () => ui.fetchAndDisplayDownloadPreview());

    // --- DYNAMIC CONTENT LISTENERS (Event Delegation) ---

    // Status tab actions (Cancel/Retry/Open/Clear)
    ui.statusContent.addEventListener('click', (event) => {
        const button = event.target.closest('button');
        if (!button) return;

        const downloadId = button.dataset.id;
        if (downloadId) {
            if (button.classList.contains('huggingface-cancel-button')) ui.handleCancelDownload(downloadId);
            else if (button.classList.contains('huggingface-retry-button')) ui.handleRetryDownload(downloadId, button);
            else if (button.classList.contains('huggingface-openpath-button')) ui.handleOpenPath(downloadId, button);
        } else if (button.id === 'huggingface-clear-history-button') {
            ui.confirmClearModal.style.display = 'flex';
        }
    });

    // Search results actions
    ui.searchResultsContainer.addEventListener('click', (event) => {
        const browseButton = event.target.closest('.huggingface-search-browse-button');
        if (browseButton) {
            const repoId = browseButton.dataset.repoId;
            if (repoId) ui.openRepoBrowser(repoId);
            return;
        }

        const downloadRepoButton = event.target.closest('.huggingface-search-download-repo-button');
        if (downloadRepoButton) {
            const repoId = downloadRepoButton.dataset.repoId;
            if (!repoId) return;
            (async () => {
                downloadRepoButton.disabled = true;
                downloadRepoButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Queueing...';
                try {
                    await ui.autoSelectModelTypeFromHuggingFace('diffusers');
                    const result = await HuggingFaceDownloaderAPI.downloadModel({
                        model_url_or_id: repoId,
                        model_type: ui.downloadModelTypeSelect.value,
                        subdir: ui.subdirSelect?.value || '',
                        save_root: ui.settings.globalRoot || '',
                        num_connections: 1,
                        force_redownload: false,
                        api_key: ui.settings.apiKey,
                    });
                    if (result && result.download_id) {
                        ui.switchTab('status');
                        ui.showToast(`Snapshot download queued: ${result.filename || repoId}`, 'success');
                    } else {
                        throw new Error(result?.error || 'No download_id returned');
                    }
                } catch (error) {
                    ui.showToast(`Failed to queue repo download: ${error.details || error.message}`, 'error');
                } finally {
                    downloadRepoButton.disabled = false;
                    downloadRepoButton.innerHTML = 'Repo <i class="fas fa-box"></i>';
                }
            })();
            return;
        }
    });

    // Pagination
    ui.searchPaginationContainer.addEventListener('click', (event) => {
        const button = event.target.closest('.huggingface-page-button');
        if (button && !button.disabled) {
            const page = parseInt(button.dataset.page, 10);
            if (page && page !== ui.searchPagination.currentPage) {
                ui.searchPagination.currentPage = page;
                ui.handleSearchSubmit();
            }
        }
    });

    // Confirmation Modal
    ui.confirmClearYesButton.addEventListener('click', () => ui.handleClearHistory());
    ui.confirmClearNoButton.addEventListener('click', () => {
        ui.confirmClearModal.style.display = 'none';
    });
    ui.confirmClearModal.addEventListener('click', (event) => {
        if (event.target === ui.confirmClearModal) {
            ui.confirmClearModal.style.display = 'none';
        }
    });
}
