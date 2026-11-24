// A block of a book made with scan-test shows its text, or, on its button, the block as printed (its scan); the
// "scans" button of a book's entry switches all its blocks. The choice of all is remembered for the next page.
function toggleScan(button) {
    const block = button.closest('.block');
    block.classList.toggle('show-scan');
    button.title = block.classList.contains('show-scan') ? 'Show the text' : 'Show the scan';
}
function toggleScans(button) {
    const blocks = button.closest('.blocks');
    const on = !blocks.classList.contains('all-scans');
    setScans(blocks, on);
    try { localStorage.setItem('bhartrhari-scans', on ? '1' : ''); } catch (e) {}
}
function setScans(blocks, on) {
    blocks.classList.toggle('all-scans', on);
    for (const block of blocks.querySelectorAll('.block')) block.classList.toggle('show-scan', on);
}
document.addEventListener('DOMContentLoaded', () => {
    let on = false;
    try { on = localStorage.getItem('bhartrhari-scans') === '1'; } catch (e) {}
    if (on) for (const blocks of document.querySelectorAll('.blocks')) setScans(blocks, true);
});
