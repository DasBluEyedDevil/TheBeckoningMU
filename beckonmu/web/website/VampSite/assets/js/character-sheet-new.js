/**
 * Vampire: The Masquerade 5th Edition Character Sheet
 * JavaScript functionality for character creation and validation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Character data model
    const character = {
        // Basic information
        name: '',
        concept: '',
        chronicle: 'The Beckoning',

        // Clan information
        clan: '',
        generation: 13,
        predator: '',

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

        // Specialties
        specialties: {},

        // Advantages (backgrounds)
        advantages: {
            allies: 0,
            contacts: 0,
            fame: 0,
            haven: 0,
            herd: 0,
            influence: 0,
            resources: 0,
            retainer: 0,
            status: 0
        },

        // Flaws
        flaws: {},

        // Derived stats
        health: 0,
        willpower: 0,
        humanity: 7,
        bloodPotency: 1,
        hunger: 1,

        // Notes
        notes: ''
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
            mental: { max: 5, priorityDots: { high: 4, medium: 3, low: 2 } },
            totalDots: 9 // 4 + 3 + 2 = 9
        },
        skills: {
            physical: { max: 5, maxAtCreation: 3, priorityDots: { high: 13, medium: 9, low: 5 } },
            social: { max: 5, maxAtCreation: 3, priorityDots: { high: 13, medium: 9, low: 5 } },
            mental: { max: 5, maxAtCreation: 3, priorityDots: { high: 13, medium: 9, low: 5 } },
            totalDots: 27 // 13 + 9 + 5 = 27
        },
        disciplines: { max: 5, maxAtCreation: 2, totalDots: 3 },
        backgrounds: { max: 5, totalDots: 7 }
    };

    // Point trackers
    const pointTrackers = {
        attributes: {
            total: validationRules.attributes.totalDots,
            used: 0,
            remaining: validationRules.attributes.totalDots,
            element: document.getElementById('attribute-points-remaining')
        },
        skills: {
            total: validationRules.skills.totalDots,
            used: 0,
            remaining: validationRules.skills.totalDots,
            element: document.getElementById('skill-points-remaining')
        },
        disciplines: {
            total: validationRules.disciplines.totalDots,
            used: 0,
            remaining: validationRules.disciplines.totalDots,
            element: document.getElementById('discipline-points-remaining')
        },
        backgrounds: {
            total: validationRules.backgrounds.totalDots,
            used: 0,
            remaining: validationRules.backgrounds.totalDots,
            element: document.getElementById('background-points-remaining')
        }
    };

    // Priority tracking for attributes and skills
    const priorityTracking = {
        attributes: {
            physical: null, // 'high', 'medium', 'low', or null
            social: null,
            mental: null
        },
        skills: {
            physical: null,
            social: null,
            mental: null
        }
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

        // Set up predator type selection
        const predatorSelect = document.getElementById('predator');
        if (predatorSelect) {
            predatorSelect.addEventListener('change', function(e) {
                character.predator = e.target.value;
            });
        }

        // Set up clan selection
        const clanSelect = document.getElementById('clan');
        clanSelect.addEventListener('change', function(e) {
            const selectedClan = e.target.value;
            character.clan = selectedClan;

            if (selectedClan && clanData[selectedClan]) {
                // Show clan details
                const clanDetails = document.getElementById('clan-details');
                if (clanDetails) {
                    clanDetails.classList.remove('hidden');
                }

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
            } else {
                // Hide clan details if no clan is selected
                const clanDetails = document.getElementById('clan-details');
                if (clanDetails) {
                    clanDetails.classList.add('hidden');
                }
            }
        });

        // Set up character submission
        const submitCharacterButton = document.getElementById('submit-character');
        if (submitCharacterButton) {
            submitCharacterButton.addEventListener('click', function() {
                // Calculate derived stats before submission
                calculateDerivedStats();

                // Validate the character before submission
                if (!validateCharacter()) {
                    return;
                }

                // Format character data according to required structure
                const formattedData = formatCharacterData(character);

                // Generate JSON
                const jsonOutput = document.getElementById('json-output');
                const characterData = JSON.stringify(formattedData, null, 2);
                jsonOutput.value = characterData;

                // Show submission status
                const submissionStatus = document.getElementById('submission-status');
                submissionStatus.textContent = "Submitting character...";
                submissionStatus.className = "submission-status processing";

                // Simulate submission (in a real app, this would be an AJAX call to a server)
                setTimeout(function() {
                    // Store the formatted character data (in a real app, this would be done on the server)
                    localStorage.setItem('character_' + Date.now(), characterData);

                    // Update submission status
                    submissionStatus.textContent = "Character submitted successfully! The Storyteller will review your character.";
                    submissionStatus.className = "submission-status success";
                }, 1500);
            });
        }

        // Function to validate the entire character before submission
        function validateCharacter() {
            // Check if name and concept are filled
            if (!character.name.trim()) {
                showError("Please enter a character name.");
                return false;
            }

            if (!character.concept.trim()) {
                showError("Please enter a character concept.");
                return false;
            }

            // Check if clan is selected
            if (!character.clan) {
                showError("Please select a clan.");
                return false;
            }

            // Validate attributes
            if (!validateAttributes()) {
                return false;
            }

            // Validate skills
            if (!validateSkills()) {
                return false;
            }

            // Validate disciplines
            if (!validateDisciplines()) {
                return false;
            }

            // Validate backgrounds
            if (!validateBackgrounds()) {
                return false;
            }

            return true;
        }

        // Set up specialties
        const addSpecialtyButton = document.getElementById('add-specialty');
        const specialtySkillSelect = document.getElementById('specialty-skill');
        const specialtyNameInput = document.getElementById('specialty-name');
        const specialtiesList = document.getElementById('specialties-list');

        if (addSpecialtyButton && specialtySkillSelect && specialtyNameInput && specialtiesList) {
            addSpecialtyButton.addEventListener('click', function() {
                const skill = specialtySkillSelect.value;
                const specialtyName = specialtyNameInput.value.trim();

                if (!skill) {
                    showError("Please select a skill for the specialty.");
                    return;
                }

                if (!specialtyName) {
                    showError("Please enter a name for the specialty.");
                    return;
                }

                // Initialize the skill in specialties if it doesn't exist
                if (!character.specialties[skill]) {
                    character.specialties[skill] = {};
                }

                // Add the specialty
                character.specialties[skill][specialtyName] = 1;

                // Create a tag element
                const tag = document.createElement('div');
                tag.className = 'tag';
                tag.innerHTML = `
                    <span class="tag-name">${skill}</span>
                    <span class="tag-value">${specialtyName}</span>
                    <span class="tag-remove" data-skill="${skill}" data-specialty="${specialtyName}">×</span>
                `;

                // Add the tag to the list
                specialtiesList.appendChild(tag);

                // Add event listener to remove button
                const removeButton = tag.querySelector('.tag-remove');
                removeButton.addEventListener('click', function() {
                    const skill = this.dataset.skill;
                    const specialty = this.dataset.specialty;

                    // Remove the specialty from the character data
                    if (character.specialties[skill] && character.specialties[skill][specialty]) {
                        delete character.specialties[skill][specialty];
                    }

                    // Remove the tag from the DOM
                    tag.remove();
                });

                // Clear the inputs
                specialtyNameInput.value = '';
            });
        }

        // Set up flaws
        const addFlawButton = document.getElementById('add-flaw');
        const flawNameInput = document.getElementById('flaw-name');
        const flawRatingSelect = document.getElementById('flaw-rating');
        const flawsList = document.getElementById('flaws-list');

        if (addFlawButton && flawNameInput && flawRatingSelect && flawsList) {
            addFlawButton.addEventListener('click', function() {
                const flawName = flawNameInput.value.trim().toLowerCase();
                const flawRating = parseInt(flawRatingSelect.value);

                if (!flawName) {
                    showError("Please enter a name for the flaw.");
                    return;
                }

                // Add the flaw
                character.flaws[flawName] = flawRating;

                // Create a tag element
                const tag = document.createElement('div');
                tag.className = 'tag';
                tag.innerHTML = `
                    <span class="tag-name">${flawName}</span>
                    <span class="tag-value">Rating: ${flawRating}</span>
                    <span class="tag-remove" data-flaw="${flawName}">×</span>
                `;

                // Add the tag to the list
                flawsList.appendChild(tag);

                // Add event listener to remove button
                const removeButton = tag.querySelector('.tag-remove');
                removeButton.addEventListener('click', function() {
                    const flaw = this.dataset.flaw;

                    // Remove the flaw from the character data
                    if (character.flaws[flaw]) {
                        delete character.flaws[flaw];
                    }

                    // Remove the tag from the DOM
                    tag.remove();
                });

                // Clear the inputs
                flawNameInput.value = '';
            });
        }

        // Set up notes
        const notesTextarea = document.getElementById('character-notes');
        if (notesTextarea) {
            notesTextarea.addEventListener('input', function(e) {
                character.notes = e.target.value;
            });
        }

        // Initialize dot selection for any existing dot elements
        initializeDotSelectors();
    }

    // Calculate derived stats based on attributes
    function calculateDerivedStats() {
        // Health = 3 + Stamina
        character.health = 3 + character.attributes.physical.stamina;

        // Willpower = Resolve + Composure
        character.willpower = character.attributes.mental.resolve + character.attributes.social.composure;

        // Update the UI
        const healthElement = document.getElementById('health');
        const willpowerElement = document.getElementById('willpower');

        if (healthElement) {
            healthElement.value = character.health;
        }

        if (willpowerElement) {
            willpowerElement.value = character.willpower;
        }
    }

    // Update point trackers
    function updatePointTracker(type) {
        const tracker = pointTrackers[type];
        if (tracker && tracker.element) {
            tracker.element.textContent = `Points remaining: ${tracker.remaining}`;

            // Add visual feedback
            if (tracker.remaining < 0) {
                tracker.element.classList.add('error');
            } else {
                tracker.element.classList.remove('error');
            }
        }
    }

    // Show error message
    function showError(message) {
        // Create error element if it doesn't exist
        let errorElement = document.getElementById('error-message');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.id = 'error-message';
            errorElement.className = 'error-message';
            document.body.appendChild(errorElement);
        }

        // Show error message
        errorElement.textContent = message;
        errorElement.classList.add('visible');

        // Hide after 3 seconds
        setTimeout(() => {
            errorElement.classList.remove('visible');
        }, 3000);
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
                        const oldValue = character.attributes[category][attribute];
                        let newValue = index + 1;

                        // Allow deselecting by clicking on the currently selected dot
                        if (oldValue === newValue) {
                            newValue = 0;
                        }

                        // Calculate point change
                        const pointChange = newValue - oldValue;

                        // Check if we have enough points
                        if (pointTrackers.attributes.remaining - pointChange < 0) {
                            showError(`You don't have enough attribute points remaining.`);
                            return;
                        }

                        // Update visual state
                        updateDots(dots, newValue > 0 ? index : -1);

                        // Update character data
                        character.attributes[category][attribute] = newValue;

                        // Update point tracker
                        pointTrackers.attributes.used += pointChange;
                        pointTrackers.attributes.remaining = pointTrackers.attributes.total - pointTrackers.attributes.used;
                        updatePointTracker('attributes');

                        // Validate attribute distribution
                        validateAttributes();

                        // Update derived stats
                        calculateDerivedStats();
                    });
                });
            } else if (container.dataset.skill) {
                // This is a skill dot container
                const skill = container.dataset.skill;

                dots.forEach((dot, index) => {
                    dot.addEventListener('click', function() {
                        const oldValue = character.skills[category][skill];
                        let newValue = index + 1;

                        // Allow deselecting by clicking on the currently selected dot
                        if (oldValue === newValue) {
                            newValue = 0;
                        }

                        // Calculate point change
                        const pointChange = newValue - oldValue;

                        // Check if we have enough points
                        if (pointTrackers.skills.remaining - pointChange < 0) {
                            showError(`You don't have enough skill points remaining.`);
                            return;
                        }

                        // Check if exceeds max at creation
                        if (newValue > validationRules.skills[category].maxAtCreation) {
                            showError(`Skills cannot exceed ${validationRules.skills[category].maxAtCreation} dots during character creation.`);
                            return;
                        }

                        // Update visual state
                        updateDots(dots, newValue > 0 ? index : -1);

                        // Update character data
                        character.skills[category][skill] = newValue;

                        // Update point tracker
                        pointTrackers.skills.used += pointChange;
                        pointTrackers.skills.remaining = pointTrackers.skills.total - pointTrackers.skills.used;
                        updatePointTracker('skills');

                        // Validate skill distribution
                        validateSkills();
                    });
                });
            } else if (container.dataset.background) {
                // This is a background dot container
                const background = container.dataset.background;

                dots.forEach((dot, index) => {
                    dot.addEventListener('click', function() {
                        const oldValue = character.backgrounds[background];
                        let newValue = index + 1;

                        // Allow deselecting by clicking on the currently selected dot
                        if (oldValue === newValue) {
                            newValue = 0;
                        }

                        // Calculate point change
                        const pointChange = newValue - oldValue;

                        // Check if we have enough points
                        if (pointTrackers.backgrounds.remaining - pointChange < 0) {
                            showError(`You don't have enough background points remaining.`);
                            return;
                        }

                        // Update visual state
                        updateDots(dots, newValue > 0 ? index : -1);

                        // Update character data
                        character.backgrounds[background] = newValue;

                        // Update point tracker
                        pointTrackers.backgrounds.used += pointChange;
                        pointTrackers.backgrounds.remaining = pointTrackers.backgrounds.total - pointTrackers.backgrounds.used;
                        updatePointTracker('backgrounds');

                        // Validate background distribution
                        validateBackgrounds();
                    });
                });
            } else if (container.dataset.advantage) {
                // This is an advantage dot container
                const advantage = container.dataset.advantage;

                dots.forEach((dot, index) => {
                    dot.addEventListener('click', function() {
                        const oldValue = character.advantages[advantage] || 0;
                        let newValue = index + 1;

                        // Allow deselecting by clicking on the currently selected dot
                        if (oldValue === newValue) {
                            newValue = 0;
                        }

                        // Update visual state
                        updateDots(dots, newValue > 0 ? index : -1);

                        // Update character data
                        character.advantages[advantage] = newValue;
                    });
                });
            } else if (container.dataset.discipline) {
                // This is a discipline dot container
                const discipline = container.dataset.discipline;

                dots.forEach((dot, index) => {
                    dot.addEventListener('click', function() {
                        const oldValue = character.disciplines[discipline];
                        let newValue = index + 1;

                        // Allow deselecting by clicking on the currently selected dot
                        if (oldValue === newValue) {
                            newValue = 0;
                        }

                        // Calculate point change
                        const pointChange = newValue - oldValue;

                        // Check if we have enough points
                        if (pointTrackers.disciplines.remaining - pointChange < 0) {
                            showError(`You don't have enough discipline points remaining.`);
                            return;
                        }

                        // Check if exceeds max at creation
                        if (newValue > validationRules.disciplines.maxAtCreation) {
                            showError(`Disciplines cannot exceed ${validationRules.disciplines.maxAtCreation} dots during character creation.`);
                            return;
                        }

                        // Update visual state
                        updateDots(dots, newValue > 0 ? index : -1);

                        // Update character data
                        character.disciplines[discipline] = newValue;

                        // Update point tracker
                        pointTrackers.disciplines.used += pointChange;
                        pointTrackers.disciplines.remaining = pointTrackers.disciplines.total - pointTrackers.disciplines.used;
                        updatePointTracker('disciplines');

                        // Validate discipline distribution
                        validateDisciplines();
                    });
                });
            }
        });
    }

    // Update disciplines based on clan selection
    function updateDisciplines(clan) {
        // Reset discipline points
        pointTrackers.disciplines.used = 0;
        pointTrackers.disciplines.remaining = pointTrackers.disciplines.total;
        updatePointTracker('disciplines');

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
    function validateAttributes() {
        // Count dots in each category
        const physicalDots = Object.values(character.attributes.physical).reduce((a, b) => a + b, 0);
        const socialDots = Object.values(character.attributes.social).reduce((a, b) => a + b, 0);
        const mentalDots = Object.values(character.attributes.mental).reduce((a, b) => a + b, 0);

        // Determine priorities based on dot counts
        const categoryDots = {
            physical: physicalDots,
            social: socialDots,
            mental: mentalDots
        };

        // Sort categories by dot count (descending)
        const sortedCategories = Object.entries(categoryDots)
            .sort((a, b) => b[1] - a[1])
            .map(entry => entry[0]);

        // Assign priorities
        if (sortedCategories.length >= 3) {
            priorityTracking.attributes[sortedCategories[0]] = 'high';
            priorityTracking.attributes[sortedCategories[1]] = 'medium';
            priorityTracking.attributes[sortedCategories[2]] = 'low';
        }

        // Update priority display in the UI
        updateAttributePriorityDisplay();

        // Check if any category exceeds its priority limit
        let valid = true;

        if (priorityTracking.attributes.physical === 'high' && physicalDots > validationRules.attributes.physical.priorityDots.high) {
            showError(`Physical attributes cannot exceed ${validationRules.attributes.physical.priorityDots.high} dots as high priority.`);
            valid = false;
        } else if (priorityTracking.attributes.physical === 'medium' && physicalDots > validationRules.attributes.physical.priorityDots.medium) {
            showError(`Physical attributes cannot exceed ${validationRules.attributes.physical.priorityDots.medium} dots as medium priority.`);
            valid = false;
        } else if (priorityTracking.attributes.physical === 'low' && physicalDots > validationRules.attributes.physical.priorityDots.low) {
            showError(`Physical attributes cannot exceed ${validationRules.attributes.physical.priorityDots.low} dots as low priority.`);
            valid = false;
        }

        if (priorityTracking.attributes.social === 'high' && socialDots > validationRules.attributes.social.priorityDots.high) {
            showError(`Social attributes cannot exceed ${validationRules.attributes.social.priorityDots.high} dots as high priority.`);
            valid = false;
        } else if (priorityTracking.attributes.social === 'medium' && socialDots > validationRules.attributes.social.priorityDots.medium) {
            showError(`Social attributes cannot exceed ${validationRules.attributes.social.priorityDots.medium} dots as medium priority.`);
            valid = false;
        } else if (priorityTracking.attributes.social === 'low' && socialDots > validationRules.attributes.social.priorityDots.low) {
            showError(`Social attributes cannot exceed ${validationRules.attributes.social.priorityDots.low} dots as low priority.`);
            valid = false;
        }

        if (priorityTracking.attributes.mental === 'high' && mentalDots > validationRules.attributes.mental.priorityDots.high) {
            showError(`Mental attributes cannot exceed ${validationRules.attributes.mental.priorityDots.high} dots as high priority.`);
            valid = false;
        } else if (priorityTracking.attributes.mental === 'medium' && mentalDots > validationRules.attributes.mental.priorityDots.medium) {
            showError(`Mental attributes cannot exceed ${validationRules.attributes.mental.priorityDots.medium} dots as medium priority.`);
            valid = false;
        } else if (priorityTracking.attributes.mental === 'low' && mentalDots > validationRules.attributes.mental.priorityDots.low) {
            showError(`Mental attributes cannot exceed ${validationRules.attributes.mental.priorityDots.low} dots as low priority.`);
            valid = false;
        }

        return valid;
    }

    // Update the attribute priority display in the UI
    function updateAttributePriorityDisplay() {
        const physicalPriorityElement = document.getElementById('physical-priority');
        const socialPriorityElement = document.getElementById('social-priority');
        const mentalPriorityElement = document.getElementById('mental-priority');

        if (physicalPriorityElement && priorityTracking.attributes.physical) {
            const priority = priorityTracking.attributes.physical;
            const maxDots = validationRules.attributes.physical.priorityDots[priority];
            physicalPriorityElement.textContent = `${priority.charAt(0).toUpperCase() + priority.slice(1)} Priority (Max ${maxDots} dots)`;
        }

        if (socialPriorityElement && priorityTracking.attributes.social) {
            const priority = priorityTracking.attributes.social;
            const maxDots = validationRules.attributes.social.priorityDots[priority];
            socialPriorityElement.textContent = `${priority.charAt(0).toUpperCase() + priority.slice(1)} Priority (Max ${maxDots} dots)`;
        }

        if (mentalPriorityElement && priorityTracking.attributes.mental) {
            const priority = priorityTracking.attributes.mental;
            const maxDots = validationRules.attributes.mental.priorityDots[priority];
            mentalPriorityElement.textContent = `${priority.charAt(0).toUpperCase() + priority.slice(1)} Priority (Max ${maxDots} dots)`;
        }
    }

    function validateSkills() {
        // Count dots in each category
        const physicalDots = Object.values(character.skills.physical).reduce((a, b) => a + b, 0);
        const socialDots = Object.values(character.skills.social).reduce((a, b) => a + b, 0);
        const mentalDots = Object.values(character.skills.mental).reduce((a, b) => a + b, 0);

        // Determine priorities based on dot counts
        const categoryDots = {
            physical: physicalDots,
            social: socialDots,
            mental: mentalDots
        };

        // Sort categories by dot count (descending)
        const sortedCategories = Object.entries(categoryDots)
            .sort((a, b) => b[1] - a[1])
            .map(entry => entry[0]);

        // Assign priorities
        if (sortedCategories.length >= 3) {
            priorityTracking.skills[sortedCategories[0]] = 'high';
            priorityTracking.skills[sortedCategories[1]] = 'medium';
            priorityTracking.skills[sortedCategories[2]] = 'low';
        }

        // Update priority display in the UI
        updateSkillsPriorityDisplay();

        // Check if any category exceeds its priority limit
        let valid = true;

        if (priorityTracking.skills.physical === 'high' && physicalDots > validationRules.skills.physical.priorityDots.high) {
            showError(`Physical skills cannot exceed ${validationRules.skills.physical.priorityDots.high} dots as high priority.`);
            valid = false;
        } else if (priorityTracking.skills.physical === 'medium' && physicalDots > validationRules.skills.physical.priorityDots.medium) {
            showError(`Physical skills cannot exceed ${validationRules.skills.physical.priorityDots.medium} dots as medium priority.`);
            valid = false;
        } else if (priorityTracking.skills.physical === 'low' && physicalDots > validationRules.skills.physical.priorityDots.low) {
            showError(`Physical skills cannot exceed ${validationRules.skills.physical.priorityDots.low} dots as low priority.`);
            valid = false;
        }

        if (priorityTracking.skills.social === 'high' && socialDots > validationRules.skills.social.priorityDots.high) {
            showError(`Social skills cannot exceed ${validationRules.skills.social.priorityDots.high} dots as high priority.`);
            valid = false;
        } else if (priorityTracking.skills.social === 'medium' && socialDots > validationRules.skills.social.priorityDots.medium) {
            showError(`Social skills cannot exceed ${validationRules.skills.social.priorityDots.medium} dots as medium priority.`);
            valid = false;
        } else if (priorityTracking.skills.social === 'low' && socialDots > validationRules.skills.social.priorityDots.low) {
            showError(`Social skills cannot exceed ${validationRules.skills.social.priorityDots.low} dots as low priority.`);
            valid = false;
        }

        if (priorityTracking.skills.mental === 'high' && mentalDots > validationRules.skills.mental.priorityDots.high) {
            showError(`Mental skills cannot exceed ${validationRules.skills.mental.priorityDots.high} dots as high priority.`);
            valid = false;
        } else if (priorityTracking.skills.mental === 'medium' && mentalDots > validationRules.skills.mental.priorityDots.medium) {
            showError(`Mental skills cannot exceed ${validationRules.skills.mental.priorityDots.medium} dots as medium priority.`);
            valid = false;
        } else if (priorityTracking.skills.mental === 'low' && mentalDots > validationRules.skills.mental.priorityDots.low) {
            showError(`Mental skills cannot exceed ${validationRules.skills.mental.priorityDots.low} dots as low priority.`);
            valid = false;
        }

        return valid;
    }

    // Update the skills priority display in the UI
    function updateSkillsPriorityDisplay() {
        const physicalPriorityElement = document.getElementById('physical-skills-priority');
        const socialPriorityElement = document.getElementById('social-skills-priority');
        const mentalPriorityElement = document.getElementById('mental-skills-priority');

        if (physicalPriorityElement && priorityTracking.skills.physical) {
            const priority = priorityTracking.skills.physical;
            const maxDots = validationRules.skills.physical.priorityDots[priority];
            physicalPriorityElement.textContent = `${priority.charAt(0).toUpperCase() + priority.slice(1)} Priority (Max ${maxDots} dots)`;
        }

        if (socialPriorityElement && priorityTracking.skills.social) {
            const priority = priorityTracking.skills.social;
            const maxDots = validationRules.skills.social.priorityDots[priority];
            socialPriorityElement.textContent = `${priority.charAt(0).toUpperCase() + priority.slice(1)} Priority (Max ${maxDots} dots)`;
        }

        if (mentalPriorityElement && priorityTracking.skills.mental) {
            const priority = priorityTracking.skills.mental;
            const maxDots = validationRules.skills.mental.priorityDots[priority];
            mentalPriorityElement.textContent = `${priority.charAt(0).toUpperCase() + priority.slice(1)} Priority (Max ${maxDots} dots)`;
        }
    }

    function validateDisciplines() {
        // Just check total dots for now
        const totalDots = Object.values(character.disciplines).reduce((a, b) => a + b, 0);

        if (totalDots > validationRules.disciplines.totalDots) {
            showError(`You can only assign ${validationRules.disciplines.totalDots} total dots to disciplines during character creation.`);
            return false;
        }

        return true;
    }

    function validateBackgrounds() {
        // Just check total dots for now
        const totalDots = Object.values(character.backgrounds).reduce((a, b) => a + b, 0);

        if (totalDots > validationRules.backgrounds.totalDots) {
            showError(`You can only assign ${validationRules.backgrounds.totalDots} total dots to backgrounds during character creation.`);
            return false;
        }

        return true;
    }

    // Format character data according to the required structure
    function formatCharacterData(char) {
        // Create the formatted data structure
        const formatted = {
            splat: "vampire",
            bio: {
                "full name": char.name,
                concept: char.concept,
                clan: char.clan,
                generation: char.generation,
                predator: char.predator
            },
            attributes: {
                strength: char.attributes.physical.strength,
                dexterity: char.attributes.physical.dexterity,
                stamina: char.attributes.physical.stamina,
                charisma: char.attributes.social.charisma,
                manipulation: char.attributes.social.manipulation,
                composure: char.attributes.social.composure,
                intelligence: char.attributes.mental.intelligence,
                wits: char.attributes.mental.wits,
                resolve: char.attributes.mental.resolve
            },
            skills: {},
            disciplines: {},
            specialties: {},
            advantages: {},
            flaws: {},
            pools: {
                health: char.health,
                willpower: char.willpower,
                humanity: char.humanity,
                "blood potency": char.bloodPotency
            },
            notes: char.notes
        };

        // Add skills (only include those with values)
        for (const category in char.skills) {
            for (const skill in char.skills[category]) {
                if (char.skills[category][skill] > 0) {
                    formatted.skills[skill] = char.skills[category][skill];
                }
            }
        }

        // Add disciplines (only include those with values)
        for (const discipline in char.disciplines) {
            if (char.disciplines[discipline] > 0) {
                formatted.disciplines[discipline] = char.disciplines[discipline];
            }
        }

        // Add specialties (only include those with values)
        for (const skill in char.specialties) {
            if (Object.keys(char.specialties[skill]).length > 0) {
                formatted.specialties[skill] = {};
                for (const specialty in char.specialties[skill]) {
                    formatted.specialties[skill][specialty] = char.specialties[skill][specialty];
                }
            }
        }

        // Add advantages (only include those with values)
        for (const advantage in char.advantages) {
            if (char.advantages[advantage] > 0) {
                formatted.advantages[advantage] = char.advantages[advantage];
            }
        }

        // Add flaws (only include those with values)
        for (const flaw in char.flaws) {
            if (char.flaws[flaw] > 0) {
                formatted.flaws[flaw] = char.flaws[flaw];
            }
        }

        return formatted;
    }

    // Initialize the form when the DOM is loaded
    initializeForm();
});
