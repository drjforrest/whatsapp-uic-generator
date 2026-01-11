# Customizing UIC Questions

The bot currently uses **placeholder questions** that should be customized for your specific use case.

## Current Placeholder Questions

The bot asks these 5 questions:

1. **What year were you born?** - User enters "1985", system uses last 3 digits
2. **Where was your mother born?** - User enters "Kinshasa", system uses first 4 letters
3. **What is your first name?** - User enters "Jean", system uses first 3 letters
4. **What day of the month were you born?** - User enters "15", system uses as-is
5. **What is your family name?** - User enters "Kabila", system uses first 4 letters

**Key principle**: Users provide FULL information. The system automatically extracts what it needs (first letters, last digits, etc.). Don't make users manually extract parts!

## How to Customize

### Step 1: Decide Your Questions

Choose 5 questions that:
- Collect information the person can remember consistently
- Produce enough variation to ensure uniqueness
- Are culturally appropriate for your context
- Balance privacy with identifiability

Examples for DRC healthcare context:
- First 2 letters of given name
- First 2 letters of family name
- Birth year (full or partial)
- Mother's initial or birth location
- Health zone or village name

### Step 2: Edit the Questions

Edit the file: `app/services/flow_manager.py`

Find the `STEPS` list (around line 115) and modify each `ConversationStep`:

```python
ConversationStep(
    key="first_name",  # Internal identifier (keep for now)
    question_en="Your English question here\n\nExample: ...",
    question_fr="Votre question en français ici\n\nExemple: ...",
    field_name="first_name",  # Database field (keep for now)
    validator=validate_digits_only  # Choose appropriate validator
),
```

### Step 3: Choose Validators

Available validators:

- `validate_digits_only` - Only numbers allowed
- `validate_letters_only` - Only letters allowed
- `validate_not_empty` - Any text, just not empty

To create custom validators, add them above the `FlowManager` class:

```python
def validate_birth_day(answer: str) -> tuple[bool, Optional[str]]:
    """Validate day of month (1-31)."""
    if not answer.isdigit():
        return False, "Please enter numbers only"

    day = int(answer)
    if day < 1 or day > 31:
        return False, "Day must be between 1 and 31"

    return True, None
```

### Step 4: Update Database Field Names (Optional)

For clarity, you can rename the database fields to match your questions.

**In `app/models/uic.py`**, update field names:

```python
# Change from:
normalized_first_name: Mapped[str] = ...

# To:
normalized_birth_year_last3: Mapped[str] = ...
```

**In `app/services/flow_manager.py`**, update `field_name`:

```python
ConversationStep(
    key="birth_year_last3",
    question_en="...",
    field_name="birth_year_last3",  # Match your new field name
    ...
),
```

### Step 5: Test Your Questions

1. Start the server: `./scripts/run_dev.sh`
2. Test on WhatsApp
3. Try different variations:
   - With accents (Gédéon)
   - Different cases (JEAN, jean, Jean)
   - Check duplicate detection works

### Step 6: Customize Data Extraction (Important!)

When users answer questions, the **UICService** extracts the parts it needs. You must update this extraction logic to match your questions!

Edit `app/services/uic_service.py`, find the `_generate_uic_code` method (around line 177):

```python
def _generate_uic_code(self, first_name, last_name, birth_year, mother_init, health_zone):
    # ⚠️ UPDATE THESE EXTRACTIONS TO MATCH YOUR QUESTIONS!

    # Example extractions:
    fn = first_name[:3]      # First 3 letters of answer to question 3
    ln = last_name[:4]       # First 4 letters of answer to question 2
    by = birth_year[-3:]     # Last 3 digits of answer to question 1
    mi = mother_init[:2]     # First 2 digits of answer to question 4
    hz = health_zone[:4]     # First 4 letters of answer to question 5

    # Pad if needed
    fn = fn.ljust(3, 'X')
    ln = ln.ljust(4, 'X')

    # Generate hash for uniqueness
    raw_seed = f"{first_name}{last_name}{birth_year}{mother_init}{health_zone}"
    hash_input = f"{raw_seed}{self.salt}".encode('utf-8')
    full_hash = hashlib.sha256(hash_input).hexdigest().upper()
    hash_suffix = full_hash[:5]

    # Create UIC format: customize this too!
    uic_code = f"{fn}{ln}-{by}{mi}-{hash_suffix}"

    return uic_code
```

**Important mapping:**
- Question 1 answer is stored in `first_name` parameter (misleading name, but kept for POC)
- Question 2 answer is stored in `last_name` parameter
- Question 3 answer is stored in `birth_year` parameter
- Question 4 answer is stored in `mother_init` parameter
- Question 5 answer is stored in `health_zone` parameter

The parameter names don't match the actual questions - they're just database field names. Focus on the extraction logic!

## Examples

### Example 1: Full Names Approach

```python
ConversationStep(
    key="given_name",
    question_en="What is your first/given name?\n\nExample: Jean",
    question_fr="Quel est votre prénom?\n\nExemple: Jean",
    field_name="given_name",
    validator=validate_letters_only
),
```

### Example 2: Numeric Code Approach

```python
ConversationStep(
    key="clinic_id",
    question_en="What is your 5-digit clinic registration number?\n\nExample: 12345",
    question_fr="Quel est votre numéro d'enregistrement clinique à 5 chiffres?\n\nExemple: 12345",
    field_name="clinic_id",
    validator=validate_clinic_id  # Custom validator
),
```

### Example 3: Mixed Approach

```python
# Question 1: Letters
ConversationStep(
    key="initials",
    question_en="What are your initials? (First and Last)\n\nExample: JK",
    field_name="initials",
    validator=validate_letters_only
),

# Question 2: Numbers
ConversationStep(
    key="birth_year",
    question_en="What year were you born?\n\nExample: 1985",
    field_name="birth_year",
    validator=validate_year
),

# Question 3: Location
ConversationStep(
    key="birth_location",
    question_en="Where were you born? (City/Village)\n\nExample: Kinshasa",
    field_name="birth_location",
    validator=validate_not_empty
),
```

## Important Notes

1. **Database Migration**: If you change field names, you'll need to:
   - Drop the existing database: `rm uic_database.db`
   - Recreate: `python scripts/init_db.py`

2. **Existing UICs**: Changing questions will generate different UICs for the same person. Plan migrations carefully.

3. **Privacy**: Consider which data points provide the best balance of uniqueness and privacy for your context.

4. **Testing**: Always test with:
   - Accented characters (é, ç, à)
   - Different cases
   - Duplicate entries to verify consistency

## Need Help?

The current placeholder questions demonstrate:
- Input validation (digits vs letters)
- Bilingual support (English/French)
- Clear examples for users
- Proper formatting

Use them as a template for your custom questions!

---

**Remember**: The UIC generation logic automatically handles:
- Accent removal (Gédéon → GEDEON)
- Case normalization (jean → JEAN)
- Special character removal (N'Djamena → NDJAMENA)

Your questions just need to collect the raw data - the system handles the rest!
