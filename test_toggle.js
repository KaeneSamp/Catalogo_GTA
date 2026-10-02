const groupData = { exclusive: true, items: [{id: 'cabelo1'}, {id: 'cabelo2'}] };
const activeItems = new Set();

function toggleItem(item) {
    const wasActive = activeItems.has(item.id);
    console.log(`Clicking ${item.id}. wasActive: ${wasActive}`);

    if (groupData.exclusive) {
        groupData.items.forEach(other => {
            activeItems.delete(other.id);
            // ui logic mock
        });
        
        if (!wasActive) {
            activeItems.add(item.id);
            // ui logic mock
        }
    }
    console.log(`State after click: ${Array.from(activeItems)}`);
}

toggleItem({id: 'cabelo1'});
toggleItem({id: 'cabelo1'});
toggleItem({id: 'cabelo2'});
