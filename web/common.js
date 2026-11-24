// A block of a book made with scan-test shows its text or the block as printed (its scan), by its switch; the switch
// at the head of a book's entry sets all its blocks, and shows which way they all are (neither, when they differ). The
// choice made for all is remembered for the next page.
function setView(block, view) {
    block.classList.toggle('show-scan', view === 'scan');
    for (const button of block.querySelectorAll(':scope > .view-switch button'))
        button.setAttribute('aria-pressed', String(button.classList.contains(view === 'scan' ? 'v-scan' : 'v-text')));
}
function showAllSwitch(blocks) {
    const all = [...blocks.querySelectorAll('.block')].filter(block => block.querySelector('.view-switch'));
    const scans = all.filter(block => block.classList.contains('show-scan')).length;
    for (const button of blocks.querySelectorAll('.view-switch.all button'))
        button.setAttribute('aria-pressed', String(button.classList.contains('v-scan') ? scans === all.length : scans === 0));
}
function showAs(button, view) {
    const blocks = button.closest('.blocks');
    if (button.closest('.view-switch').classList.contains('all')) {
        for (const block of blocks.querySelectorAll('.block')) setView(block, view);
        try { localStorage.setItem('bhartrhari-scans', view === 'scan' ? '1' : ''); } catch (e) {}
    } else {
        setView(button.closest('.block'), view);
    }
    showAllSwitch(blocks);
}
document.addEventListener('DOMContentLoaded', () => {
    let scans = false;
    try { scans = localStorage.getItem('bhartrhari-scans') === '1'; } catch (e) {}
    if (scans) for (const blocks of document.querySelectorAll('.blocks')) {
        for (const block of blocks.querySelectorAll('.block')) setView(block, 'scan');
        showAllSwitch(blocks);
    }
});
