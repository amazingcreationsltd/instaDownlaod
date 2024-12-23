// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('a'); // Select all tab elements
    let currentTab = document.querySelector('.border-b-[#019863]'); // Get initially active tab

    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Don't do anything if clicking the current tab
            if (tab === currentTab) return;

            // Remove active classes from current tab
            currentTab.classList.remove('border-b-[#019863]', 'border-b-[4px]', 'text-[#1C160C]');
            currentTab.classList.add('border-b-transparent', 'border-b-[3px]', 'text-[#A18249]');

            // Add active classes to clicked tab
            tab.classList.remove('border-b-transparent', 'border-b-[3px]', 'text-[#A18249]');
            tab.classList.add('border-b-[#019863]', 'border-b-[4px]', 'text-[#1C160C]');

            // Update current tab
            currentTab = tab;
        });
    });
});