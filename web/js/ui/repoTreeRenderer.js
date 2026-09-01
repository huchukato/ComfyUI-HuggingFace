// Repo file browser for HuggingFace Search results.
// Usage: openRepoBrowser(uiInstance, repoId)

import { HuggingFaceDownloaderAPI } from "../api/huggingface.js";

const MODAL_ID = 'huggingface-repo-tree-modal';
const MODAL_TITLE_ID = 'huggingface-repo-tree-title';
const PATH_BREADCRUMB_ID = 'huggingface-repo-tree-breadcrumb';
const TREE_CONTENT_ID = 'huggingface-repo-tree-content';

function encodePath(path) {
  return path.split('/').map(p => encodeURIComponent(p)).join('/');
}

function getFileUrl(repoId, path) {
  return `https://huggingface.co/${repoId}/resolve/main/${encodePath(path)}`;
}

function removeExistingModal() {
  const existing = document.getElementById(MODAL_ID);
  if (existing) existing.remove();
}

function modalHtml(repoId) {
  const repoName = repoId.split('/').pop();
  return `
    <div id="${MODAL_ID}" class="huggingface-repo-tree-modal">
      <div class="huggingface-repo-tree-modal-content">
        <div class="huggingface-repo-tree-header">
          <h4 id="${MODAL_TITLE_ID}">${repoName}</h4>
          <div class="huggingface-repo-tree-actions">
            <button id="huggingface-repo-tree-download-repo" class="huggingface-button primary small" title="Download entire repo with snapshot_download">
              <i class="fas fa-download"></i> Download repo
            </button>
            <button id="huggingface-repo-tree-close" class="huggingface-button secondary small">Close</button>
          </div>
        </div>
        <div id="${PATH_BREADCRUMB_ID}" class="huggingface-repo-tree-breadcrumb"></div>
        <div id="${TREE_CONTENT_ID}" class="huggingface-repo-tree-content">
          <p><i class="fas fa-spinner fa-spin"></i> Loading repository contents...</p>
        </div>
      </div>
    </div>
  `;
}

export async function openRepoBrowser(ui, repoId) {
  removeExistingModal();
  const container = document.createElement('div');
  container.innerHTML = modalHtml(repoId);
  document.body.appendChild(container.firstElementChild);

  const modal = document.getElementById(MODAL_ID);
  const closeBtn = modal.querySelector('#huggingface-repo-tree-close');
  const downloadRepoBtn = modal.querySelector('#huggingface-repo-tree-download-repo');

  closeBtn.addEventListener('click', () => modal.remove());
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.remove();
  });
  downloadRepoBtn.addEventListener('click', () => handleDownloadRepo(ui, repoId));

  ui.ensureFontAwesome();
  await loadTreePath(ui, repoId, '');
}

async function loadTreePath(ui, repoId, path) {
  const content = document.getElementById(TREE_CONTENT_ID);
  const breadcrumb = document.getElementById(PATH_BREADCRUMB_ID);
  content.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> Loading...</p>';

  try {
    const response = await HuggingFaceDownloaderAPI.getRepoTree({
      repo_id: repoId,
      path: path,
      api_key: ui.settings.apiKey,
    });

    if (!response || !Array.isArray(response.items)) {
      throw new Error('Invalid repository tree response');
    }

    renderBreadcrumb(breadcrumb, repoId, path);
    renderTreeItems(ui, repoId, path, response.items);
  } catch (error) {
    content.innerHTML = `<p style="color: var(--error-text, #ff6b6b);">Failed to list files: ${error.details || error.message || 'Unknown error'}</p>`;
  }
}

function renderBreadcrumb(container, repoId, currentPath) {
  const parts = currentPath ? currentPath.split('/') : [];
  let html = `<button class="huggingface-repo-tree-breadcrumb-root" data-path="">${repoId.split('/').pop()}</button>`;
  let acc = '';
  parts.forEach((part, idx) => {
    acc = acc ? `${acc}/${part}` : part;
    html += ` / <button class="huggingface-repo-tree-breadcrumb-part" data-path="${acc}">${part}</button>`;
  });
  container.innerHTML = html;

  const modal = document.getElementById(MODAL_ID);
  container.querySelectorAll('button').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.path;
      const ui = modal?.__huggingface_ui;
      if (ui) loadTreePath(ui, repoId, target);
    });
  });
}

function renderTreeItems(ui, repoId, currentPath, items) {
  const content = document.getElementById(TREE_CONTENT_ID);
  const modal = document.getElementById(MODAL_ID);
  modal.__huggingface_ui = ui;

  if (items.length === 0) {
    content.innerHTML = '<p>This folder is empty.</p>';
    return;
  }

  const directories = items.filter(i => i.type === 'directory');
  const files = items.filter(i => i.type === 'file');

  const createRow = (icon, label, size, actionsHtml, dataPath, isDir) => {
    const sizeText = size !== null && size !== undefined ? ui.formatBytes(size) : '';
    return `
      <div class="huggingface-repo-tree-row ${isDir ? 'directory' : 'file'}" data-path="${dataPath}">
        <span class="huggingface-repo-tree-icon"><i class="fas ${icon}"></i></span>
        <span class="huggingface-repo-tree-label" title="${label}">${label}</span>
        <span class="huggingface-repo-tree-size">${sizeText}</span>
        <span class="huggingface-repo-tree-row-actions">${actionsHtml}</span>
      </div>
    `;
  };

  const dirRows = directories.map(dir => {
    const fullPath = currentPath ? `${currentPath}/${dir.path.split('/').pop()}` : dir.path.split('/').pop();
    return createRow('fa-folder', fullPath.split('/').pop(), null, '', fullPath, true);
  });

  const fileRows = files.map(file => {
    const fileName = file.path.split('/').pop();
    const actions = `
      <button class="huggingface-button primary tiny huggingface-tree-download-file"
              data-repo="${repoId}" data-path="${file.path}">
        <i class="fas fa-download"></i> Download
      </button>
    `;
    return createRow('fa-file', fileName, file.size, actions, file.path, false);
  });

  content.innerHTML = `
    <div class="huggingface-repo-tree-list">
      ${dirRows.join('')}
      ${fileRows.join('')}
    </div>
  `;

  ui.ensureFontAwesome();

  content.querySelectorAll('.huggingface-repo-tree-row.directory').forEach(row => {
    row.addEventListener('click', (e) => {
      if (e.target.closest('button')) return;
      const target = row.dataset.path;
      loadTreePath(ui, repoId, target);
    });
  });

  content.querySelectorAll('.huggingface-tree-download-file').forEach(btn => {
    btn.addEventListener('click', () => {
      const filePath = btn.dataset.path;
      handleDownloadFile(ui, repoId, filePath);
    });
  });
}

function handleDownloadFile(ui, repoId, filePath) {
  const url = getFileUrl(repoId, filePath);
  ui.modelUrlInput.value = url;
  ui.debounceFetchDownloadPreview?.(0);
  ui.switchTab('download');
  document.getElementById(MODAL_ID)?.remove();
  ui.showToast(`Selected ${filePath.split('/').pop()}. Review the Download tab and start.`, 'info');
}

async function handleDownloadRepo(ui, repoId) {
  const btn = document.getElementById('huggingface-repo-tree-download-repo');
  if (!btn) return;
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Queueing...';

  try {
    await ui.autoSelectModelTypeFromHuggingFace('diffusers');
  } catch (_) {
    // leave current model type
  }

  try {
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
      document.getElementById(MODAL_ID)?.remove();
    } else {
      throw new Error(result?.error || 'No download_id returned');
    }
  } catch (error) {
    ui.showToast(`Failed to queue repo download: ${error.details || error.message}`, 'error');
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-download"></i> Download repo';
  }
}
