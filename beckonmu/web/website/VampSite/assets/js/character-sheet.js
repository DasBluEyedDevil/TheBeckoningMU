/**
 * Vampire: The Masquerade 5th Edition Character Sheet
 * JavaScript functionality for character creation and validation
 */

// classList polyfill for older browsers
if (!("classList" in document.documentElement)) {
    (function() {
        var prototype = Array.prototype,
            push = prototype.push,
            splice = prototype.splice,
            join = prototype.join;

        function DOMTokenList(el) {
            this.el = el;
            var classes = el.className.replace(/^\s+|\s+$/g, '').split(/\s+/);
            for (var i = 0; i < classes.length; i++) {
                push.call(this, classes[i]);
            }
        }

        DOMTokenList.prototype = {
            add: function(token) {
                if(this.contains(token)) return;
                push.call(this, token);
                this.el.className = this.toString();
            },
            contains: function(token) {
                return this.el.className.indexOf(token) != -1;
            },
            item: function(index) {
                return this[index] || null;
            },
            remove: function(token) {
                if (!this.contains(token)) return;
                for (var i = 0; i < this.length; i++) {
                    if (this[i] == token) break;
                }
                splice.call(this, i, 1);
                this.el.className = this.toString();
            },
            toString: function() {
                return join.call(this, ' ');
            },
            toggle: function(token) {
                if (!this.contains(token)) {
                    this.add(token);
                } else {
                    this.remove(token);
                }
                return this.contains(token);
            }
        };

        window.DOMTokenList = DOMTokenList;

        function defineElementGetter(obj, prop, getter) {
            if (Object.defineProperty) {
                Object.defineProperty(obj, prop, { get: getter });
            } else {
                obj.__defineGetter__(prop, getter);
            }
        }

        defineElementGetter(Element.prototype, 'classList', function() {
            return new DOMTokenList(this);
        });
    })();
}

document.addEventListener('DOMContentLoaded', function() {
    // Character data model
    const character = {
        // Basic information
        name: '',
        concept: '',
        chronicle: 'The Beckoning',

        // Clan information
        clan: '',
        predatorType: '',

        // Attributes
        attributes: {
            physical: {
                strength: 0,
                dexterity: 0,
                stamina: 0
            },
            social: {
                charisma: 0,
                manipulation: 0,
                composure: 0
            },
            mental: {
                intelligence: 0,
                wits: 0,
                resolve: 0
            }
        },

        // Skills
        skills: {
            physical: {
                athletics: 0,
                brawl: 0,
                craft: 0,
                drive: 0,
                firearms: 0,
                melee: 0,
                stealth: 0,
                survival: 0
            },
            social: {
                animalKen: 0,
                etiquette: 0,
                insight: 0,
                intimidation: 0,
                leadership: 0,
                performance: 0,
                persuasion: 0,
                streetwise: 0,
                subterfuge: 0
            },
            mental: {
                academics: 0,
                awareness: 0,
                finance: 0,
                investigation: 0,
                medicine: 0,
                occult: 0,
                politics: 0,
                science: 0,
                technology: 0
            }
        },

        // Disciplines (will be populated based on clan)
        disciplines: {},

        // Advantages
        backgrounds: {
            allies: 0,
            contacts: 0,
            fame: 0,
            herd: 0,
            influence: 0,
            loresheet: 0,
            mask: 0,
            mawla: 0,
            resources: 0,
            retainer: 0,
            status: 0
        },

        // Derived stats
        health: 0,
        willpower: 0,
        humanity: 0,
        bloodPotency: 0,
        hunger: 0,

        // Merits and flaws
        merits: [],
        flaws: []
    };

    // Clan data
    const clanData = {
        brujah: {
            disciplines: ['potence', 'presence', 'celerity'],
            bane: 'Brujah have a harder time controlling their anger. When frenzy is a possibility, Brujah suffer a two-dice penalty to resist it.',
            compulsion: 'Rebellion: The vampire refuses to bow to any authority figure or obey any social norms for the remainder of the scene.'
        },
        gangrel: {
            disciplines: ['animalism', 'fortitude', 'protean'],
            bane: 'When a Gangrel frenzies, they gain an animal feature for a number of nights equal to the Bane Severity.',
            compulsion: 'Feral Impulses: The vampire surrenders to their animal nature for the remainder of the scene.'
        },
        malkavian: {
            disciplines: ['auspex', 'dominate', 'obfuscate'],
            bane: 'Malkavians suffer from a permanent, incurable derangement. Additionally, they have a harder time resisting their compulsion.',
            compulsion: 'Delusion: The vampire becomes convinced of something that isn\'t true for the remainder of the scene.'
        },
        nosferatu: {
            disciplines: ['animalism', 'obfuscate', 'potence'],
            bane: 'Nosferatu are hideously deformed, making it impossible to blend into mortal society without using Obfuscate.',
            compulsion: 'Cryptophilia: The vampire becomes obsessed with collecting and sharing secrets for the remainder of the scene.'
        },
        toreador: {
            disciplines: ['auspex', 'celerity', 'presence'],
            bane: 'When exposed to something beautiful, Toreador must make a Resolve + Awareness roll with difficulty equal to Bane Severity or be entranced.',
            compulsion: 'Obsession: The vampire becomes fixated on a specific thing of beauty for the remainder of the scene.'
        },
        tremere: {
            disciplines: ['auspex', 'blood sorcery', 'dominate'],
            bane: 'Tremere are bound by a blood bond to their clan and lineage. They also have a harder time creating blood bonds with others.',
            compulsion: 'Perfectionism: The vampire becomes obsessed with performing a task flawlessly for the remainder of the scene.'
        },
        ventrue: {
            disciplines: ['dominate', 'fortitude', 'presence'],
            bane: 'Ventrue can only feed from a specific type of mortal. They cannot gain sustenance from any other kind of blood.',
            compulsion: 'Arrogance: The vampire refuses to lower themselves to deal with those they consider beneath them for the remainder of the scene.'
        },
        caitiff: {
            disciplines: ['any', 'any', 'any'],
            bane: 'Caitiff suffer increased Bane Severity and have a harder time gaining status among other Kindred.',
            compulsion: 'Conformity: The vampire desperately tries to fit in with those around them for the remainder of the scene.'
        },
        'thin-blood': {
            disciplines: ['thin-blood alchemy'],
            bane: 'Thin-bloods cannot use most disciplines and suffer from various weaknesses depending on their specific condition.',
            compulsion: 'Mortality: The vampire behaves as if they were still mortal for the remainder of the scene.'
        }
    };

    // Validation rules
    const validationRules = {
        attributes: {
            physical: { max: 5, priorityDots: { high: 4, medium: 3, low: 2 } },
            social: { max: 5, priorityDots: { high: 4, medium: 3, low: 2 } },
            mental: { max: 5, priorityDots: { high: 4, medium: 3, low: 2 } }
        },
        skills: {
            physical: { max: 5, maxAtCreation: 3, priorityDots: { high: 13, medium: 9, low: 5 } },
            social: { max: 5, maxAtCreation: 3, priorityDots: { high: 13, medium: 9, low: 5 } },
            mental: { max: 5, maxAtCreation: 3, priorityDots: { high: 13, medium: 9, low: 5 } }
        },
        disciplines: { max: 5, maxAtCreation: 2, totalDots: 3 },
        backgrounds: { max: 5, totalDots: 7 }
    };

    // Initialize form elements
    function initializeForm() {
        // Set up event listeners for basic information
        document.getElementById('character-name').addEventListener('input', function(e) {
            character.name = e.target.value;
        });

        document.getElementById('concept').addEventListener('input', function(e) {
            character.concept = e.target.value;
        });

        document.getElementById('chronicle').addEventListener('input', function(e) {
            character.chronicle = e.target.value;
        });

        // Set up clan selection
        const clanSelect = document.getElementById('clan');
        clanSelect.addEventListener('change', function(e) {
            const selectedClan = e.target.value;
            character.clan = selectedClan;

            if (selectedClan && clanData[selectedClan]) {
                // Update disciplines based on clan
                updateDisciplines(selectedClan);

                // Update clan bane and compulsion if those fields exist
                const clanBaneElement = document.getElementById('clan-bane');
                const clanCompulsionElement = document.getElementById('clan-compulsion');

                if (clanBaneElement) {
                    clanBaneElement.value = clanData[selectedClan].bane;
                }

                if (clanCompulsionElement) {
                    clanCompulsionElement.value = clanData[selectedClan].compulsion;
                }
            }
        });

        // Set up JSON generation
        const generateJsonButton = document.getElementById('generate-json');
        if (generateJsonButton) {
            generateJsonButton.addEventListener('click', function() {
                const jsonOutput = document.getElementById('json-output');
                jsonOutput.value = JSON.stringify(character, null, 2);
            });
        }

        // Initialize dot selection for any existing dot elements
        initializeDotSelectors();
    }

    // Initialize dot selectors for attributes, skills, etc.
    function initializeDotSelectors() {
        const dotContainers = document.querySelectorAll('.dots');

        dotContainers.forEach(container => {
            const dots = container.querySelectorAll('.dot');
            const category = container.dataset.category;

            if (container.dataset.attribute) {
                // This is an attribute dot container
                const attribute = container.dataset.attribute;

                dots.forEach((dot, index) => {
                    dot.addEventListener('click', function() {
                        // Update visual state
                        updateDots(dots, index);

                        // Update character data
                        character.attributes[category][attribute] = index + 1;

                        // Validate attribute distribution
                        validateAttributes(category);
                    });
                });
            } else if (container.dataset.skill) {
                // This is a skill dot container
                const skill = container.dataset.skill;

                dots.forEach((dot, index) => {
                    dot.addEventListener('click', function() {
                        // Check if exceeds max at creation
                        if (index + 1 > validationRules.skills[category].maxAtCreation) {
                            alert(`Skills cannot exceed ${validationRules.skills[category].maxAtCreation} dots during character creation.`);
                            return;
                        }

                        // Update visual state
                        updateDots(dots, index);

                        // Update character data
                        character.skills[category][skill] = index + 1;

                        // Validate skill distribution
                        validateSkills(category);
                    });
                });
            } else if (container.dataset.background) {
                // This is a background dot container
                const background = container.dataset.background;

                dots.forEach((dot, index) => {
                    dot.addEventListener('click', function() {
                        // Update visual state
                        updateDots(dots, index);

                        // Update character data
                        character.backgrounds[background] = index + 1;

                        // Validate background distribution
                        validateBackgrounds();
                    });
                });
            } else if (container.dataset.discipline) {
                // This is a discipline dot container
                const discipline = container.dataset.discipline;

                dots.forEach((dot, index) => {
                    dot.addEventListener('click', function() {
                        // Check if exceeds max at creation
                        if (index + 1 > validationRules.disciplines.maxAtCreation) {
                            alert(`Disciplines cannot exceed ${validationRules.disciplines.maxAtCreation} dots during character creation.`);
                            return;
                        }

                        // Update visual state
                        updateDots(dots, index);

                        // Update character data
                        character.disciplines[discipline] = index + 1;

                        // Validate discipline distribution
                        validateDisciplines();
                    });
                });
            }
        });
    }

    // Update the visual state of dots
    function updateDots(dots, selectedIndex) {
        dots.forEach((dot, index) => {
            if (index <= selectedIndex) {
                dot.classList.add('filled');
            } else {
                dot.classList.remove('filled');
            }
        });
    }

    // Update disciplines based on clan selection
    function updateDisciplines(clan) {
        // Clear existing disciplines
        character.disciplines = {};

        // Get disciplines container
        const disciplinesContainer = document.getElementById('disciplines-container');
        if (!disciplinesContainer) return;

        // Clear container
        disciplinesContainer.innerHTML = '';

        // If no clan selected or clan not in data, return
        if (!clan || !clanData[clan]) return;

        // Get disciplines for selected clan
        const clanDisciplines = clanData[clan].disciplines;

        // Create discipline elements
        clanDisciplines.forEach(discipline => {
            // Initialize discipline in character data
            character.disciplines[discipline] = 0;

            // Create discipline element
            const disciplineElement = document.createElement('div');
            disciplineElement.className = 'form-group';
            disciplineElement.innerHTML = `
                <label for="discipline-${discipline}">${discipline.charAt(0).toUpperCase() + discipline.slice(1)}</label>
                <div class="dots" data-discipline="${discipline}">
                    <span class="dot" data-value="1"></span>
                    <span class="dot" data-value="2"></span>
                    <span class="dot" data-value="3"></span>
                    <span class="dot" data-value="4"></span>
                    <span class="dot" data-value="5"></span>
                </div>
            `;

            // Add to container
            disciplinesContainer.appendChild(disciplineElement);
        });

        // Initialize dot selectors for new disciplines
        initializeDotSelectors();
    }

    // Validation functions
    function validateAttributes(category) {
        // Implementation will depend on the specific validation rules
        // For now, just log the current state
        console.log(`Validating ${category} attributes:`, character.attributes[category]);
    }

    function validateSkills(category) {
        // Implementation will depend on the specific validation rules
        // For now, just log the current state
        console.log(`Validating ${category} skills:`, character.skills[category]);
    }

    function validateDisciplines() {
        // Implementation will depend on the specific validation rules
        // For now, just log the current state
        console.log('Validating disciplines:', character.disciplines);
    }

    function validateBackgrounds() {
        // Implementation will depend on the specific validation rules
        // For now, just log the current state
        console.log('Validating backgrounds:', character.backgrounds);
    }

    // Initialize the form when the DOM is loaded
    initializeForm();
});
