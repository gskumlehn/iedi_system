"""
IEDI Calculator v2.0

Complete implementation of IEDI (Digital Press Exposure Index) calculation
following the v2.0 methodology.

Changes from v1.0:
- Removed: Spokespersons (weight 20)
- Removed: Images (weight 20)
- Modified: Subtitle verification is now conditional (snippet != fullText)

Author: Manus AI
Date: 2024-11-13
Version: 2.0
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Bank:
    """Bank entity with name and variations."""
    id: int
    name: str
    variations: List[str]
    active: bool = True


@dataclass
class RelevantMediaOutlet:
    """Relevant media outlet entity."""
    id: int
    name: str
    domain: str
    category: str
    active: bool = True


@dataclass
class NicheMediaOutlet:
    """Niche media outlet entity."""
    id: int
    name: str
    domain: str
    category: str
    monthly_visitors: int
    active: bool = True


@dataclass
class IEDIResult:
    """Result of IEDI calculation for a single mention."""
    score: float  # 0-10 scale
    score_normalized: float  # -1 to 1 scale
    sentiment: str
    reach_group: str
    numerator: int
    denominator: int
    variables: Dict[str, any]
    subtitle_verified: bool


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_first_paragraph(full_text: str) -> str:
    """
    Extract the first paragraph from full text.
    
    Considers as paragraph:
    - Text until first double line break (\\n\\n)
    - Or first 300 characters if no double break exists
    
    Args:
        full_text: Complete text of the mention
    
    Returns:
        First paragraph as string
    """
    if not full_text:
        return ""
    
    # Split by double line breaks
    paragraphs = full_text.split('\n\n')
    
    if len(paragraphs) > 1 and paragraphs[0].strip():
        return paragraphs[0].strip()
    
    # No double breaks, take first 300 characters
    return full_text[:300].strip()


def check_bank_mention(text: str, bank: Bank) -> bool:
    """
    Check if bank is mentioned in text.
    
    Args:
        text: Text to search in
        bank: Bank object with name and variations
    
    Returns:
        True if bank is mentioned, False otherwise
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Check main name
    if bank.name.lower() in text_lower:
        return True
    
    # Check variations
    for variation in bank.variations:
        if variation.lower() in text_lower:
            return True
    
    return False


# ============================================================================
# VERIFICATION FUNCTIONS
# ============================================================================

def verify_title(title: str, bank: Bank) -> int:
    """
    Verify if bank is mentioned in the title.
    
    Args:
        title: Title of the mention
        bank: Bank object
    
    Returns:
        100 if bank is mentioned, 0 otherwise
    """
    if check_bank_mention(title, bank):
        return 100
    return 0


def verify_subtitle(snippet: str, full_text: str, bank: Bank) -> Tuple[int, bool]:
    """
    Verify if bank is mentioned in the first paragraph.
    ONLY if snippet != fullText (full text available).
    
    This conditional logic ensures we only verify subtitle when we have
    access to the complete text. When snippet == fullText, it indicates
    a paywall or very short content, and we cannot reliably extract
    the first paragraph.
    
    Args:
        snippet: Snippet of the mention (best match to query)
        full_text: Complete text of the mention
        bank: Bank object
    
    Returns:
        Tuple of (points, verification_performed)
        - (80, True) if bank mentioned and verification performed
        - (0, True) if bank not mentioned but verification performed
        - (0, False) if verification was not performed (paywall)
    """
    # Check if we have full text available
    if snippet == full_text:
        # Paywall or very short text - do not verify
        return (0, False)
    
    # Extract first paragraph
    first_paragraph = extract_first_paragraph(full_text)
    
    # Check bank mention
    if check_bank_mention(first_paragraph, bank):
        return (80, True)
    
    return (0, True)


def verify_relevant_outlet(domain: str, relevant_outlets: List[RelevantMediaOutlet]) -> int:
    """
    Verify if domain is in the relevant media outlets list.
    
    Args:
        domain: Domain of the mention (e.g., "valor.globo.com")
        relevant_outlets: List of relevant media outlets
    
    Returns:
        95 if relevant outlet, 0 otherwise
    """
    if not domain:
        return 0
    
    domain_lower = domain.lower()
    
    for outlet in relevant_outlets:
        if not outlet.active:
            continue
        
        outlet_domain_lower = outlet.domain.lower()
        
        # Check if domain matches
        if domain_lower.endswith(outlet_domain_lower) or outlet_domain_lower in domain_lower:
            return 95
    
    return 0


def verify_niche_outlet(domain: str, niche_outlets: List[NicheMediaOutlet]) -> int:
    """
    Verify if domain is in the niche media outlets list.
    
    Args:
        domain: Domain of the mention
        niche_outlets: List of niche media outlets
    
    Returns:
        54 if niche outlet, 0 otherwise
    """
    if not domain:
        return 0
    
    domain_lower = domain.lower()
    
    for outlet in niche_outlets:
        if not outlet.active:
            continue
        
        outlet_domain_lower = outlet.domain.lower()
        
        # Check if domain matches
        if domain_lower.endswith(outlet_domain_lower) or outlet_domain_lower in domain_lower:
            return 54
    
    return 0


def classify_reach_group(monthly_visitors: int) -> Tuple[str, int]:
    """
    Classify media outlet into reach group based on monthly visitors.
    
    Groups:
    - A: > 29,000,000 visitors (weight 91)
    - B: 11,000,001 - 29,000,000 visitors (weight 85)
    - C: 500,000 - 11,000,000 visitors (weight 24)
    - D: 0 - 500,000 visitors (weight 20)
    
    Args:
        monthly_visitors: Number of unique monthly visitors
    
    Returns:
        Tuple of (group_letter, weight)
    """
    if monthly_visitors > 29_000_000:
        return ("A", 91)
    elif monthly_visitors > 11_000_000:
        return ("B", 85)
    elif monthly_visitors >= 500_000:
        return ("C", 24)
    else:
        return ("D", 20)


# ============================================================================
# MAIN CALCULATION FUNCTION
# ============================================================================

def calculate_mention_iedi(
    mention: Dict,
    bank: Bank,
    relevant_outlets: List[RelevantMediaOutlet],
    niche_outlets: List[NicheMediaOutlet]
) -> IEDIResult:
    """
    Calculate IEDI for a single mention following v2.0 methodology.
    
    This function implements the complete IEDI calculation including:
    - Conditional subtitle verification (snippet != fullText)
    - Proper denominator calculation based on reach group
    - Sentiment-based sign application
    - Conversion to 0-10 scale
    
    Args:
        mention: Dictionary with mention data from Brandwatch API
        bank: Bank object being analyzed
        relevant_outlets: List of relevant media outlets
        niche_outlets: List of niche media outlets
    
    Returns:
        IEDIResult object with complete calculation details
    
    Example mention dict:
        {
            "sentiment": "positive",
            "title": "Banco do Brasil anuncia lucro recorde",
            "snippet": "O Banco do Brasil divulgou...",
            "fullText": "O Banco do Brasil divulgou ontem seus resultados...",
            "domain": "valor.globo.com",
            "monthlyVisitors": 14000000
        }
    """
    # ========================================================================
    # 1. EXTRACT FIELDS FROM MENTION
    # ========================================================================
    
    sentiment = mention.get("sentiment", "neutral")
    title = mention.get("title", "")
    snippet = mention.get("snippet", "")
    full_text = mention.get("fullText", snippet)  # Fallback to snippet if no fullText
    domain = mention.get("domain", "")
    monthly_visitors = mention.get("monthlyVisitors", 0)
    
    # ========================================================================
    # 2. PERFORM VERIFICATIONS
    # ========================================================================
    
    # Title verification (always performed)
    title_points = verify_title(title, bank)
    title_verified = title_points > 0
    
    # Subtitle verification (conditional)
    subtitle_points, subtitle_verified = verify_subtitle(snippet, full_text, bank)
    
    # Relevant outlet verification (always performed)
    relevant_outlet_points = verify_relevant_outlet(domain, relevant_outlets)
    relevant_outlet_verified = relevant_outlet_points > 0
    
    # Niche outlet verification (always performed)
    niche_outlet_points = verify_niche_outlet(domain, niche_outlets)
    niche_outlet_verified = niche_outlet_points > 0
    
    # Reach group classification (always performed)
    reach_group, reach_group_points = classify_reach_group(monthly_visitors)
    
    # ========================================================================
    # 3. CALCULATE NUMERATOR
    # ========================================================================
    
    numerator = (
        title_points +
        subtitle_points +
        reach_group_points +
        relevant_outlet_points +
        niche_outlet_points
    )
    
    # ========================================================================
    # 4. CALCULATE DENOMINATOR
    # ========================================================================
    
    # Base denominator components
    title_weight = 100
    subtitle_weight = 80
    relevant_outlet_weight = 95
    niche_outlet_weight = 54
    
    # Start with title and reach group (always included)
    denominator = title_weight + reach_group_points + relevant_outlet_weight
    
    # Add subtitle weight ONLY if verification was performed
    if subtitle_verified:
        denominator += subtitle_weight
    
    # Add niche outlet weight for groups B, C, D (NOT for group A)
    if reach_group != "A":
        denominator += niche_outlet_weight
    
    # ========================================================================
    # 5. APPLY SENTIMENT SIGN
    # ========================================================================
    
    if sentiment == "positive":
        sign = 1
    elif sentiment == "negative":
        sign = -1
    else:  # neutral
        sign = 0
    
    # ========================================================================
    # 6. CALCULATE IEDI (-1 to 1 scale)
    # ========================================================================
    
    if denominator > 0 and sign != 0:
        iedi_normalized = (numerator / denominator) * sign
    else:
        iedi_normalized = 0.0
    
    # ========================================================================
    # 7. CONVERT TO 0-10 SCALE
    # ========================================================================
    
    iedi_score = ((iedi_normalized + 1) / 2) * 10
    
    # ========================================================================
    # 8. BUILD RESULT
    # ========================================================================
    
    result = IEDIResult(
        score=round(iedi_score, 2),
        score_normalized=round(iedi_normalized, 4),
        sentiment=sentiment,
        reach_group=reach_group,
        numerator=numerator,
        denominator=denominator,
        variables={
            "title": title_verified,
            "subtitle": subtitle_verified if subtitle_verified is not False else None,
            "relevant_outlet": relevant_outlet_verified,
            "niche_outlet": niche_outlet_verified,
            "reach_group": reach_group,
            "reach_group_points": reach_group_points
        },
        subtitle_verified=subtitle_verified
    )
    
    return result


# ============================================================================
# AGGREGATION FUNCTIONS
# ============================================================================

def calculate_average_iedi(iedi_results: List[IEDIResult]) -> float:
    """
    Calculate average IEDI from multiple mention results.
    
    Args:
        iedi_results: List of IEDIResult objects
    
    Returns:
        Average IEDI score (0-10 scale)
    """
    if not iedi_results:
        return 0.0
    
    total = sum(result.score for result in iedi_results)
    return round(total / len(iedi_results), 2)


def calculate_final_iedi(
    iedi_results: List[IEDIResult],
    positive_volume: int,
    total_volume: int
) -> float:
    """
    Calculate final IEDI with positivity balancing.
    
    Final IEDI = Average IEDI × (Positive Volume / Total Volume)
    
    This balancing penalizes banks with many negative mentions,
    even if they have high exposure.
    
    Args:
        iedi_results: List of IEDIResult objects
        positive_volume: Number of positive mentions
        total_volume: Total number of mentions
    
    Returns:
        Final IEDI score (0-10 scale)
    """
    if total_volume == 0:
        return 0.0
    
    average_iedi = calculate_average_iedi(iedi_results)
    positivity_ratio = positive_volume / total_volume
    
    final_iedi = average_iedi * positivity_ratio
    
    return round(final_iedi, 2)


def aggregate_bank_results(
    iedi_results: List[IEDIResult]
) -> Dict:
    """
    Aggregate IEDI results for a bank in a period.
    
    Args:
        iedi_results: List of IEDIResult objects for the bank
    
    Returns:
        Dictionary with aggregated metrics
    """
    if not iedi_results:
        return {
            "total_volume": 0,
            "positive_volume": 0,
            "negative_volume": 0,
            "neutral_volume": 0,
            "average_iedi": 0.0,
            "final_iedi": 0.0,
            "positivity_rate": 0.0,
            "negativity_rate": 0.0
        }
    
    # Count by sentiment
    positive_volume = sum(1 for r in iedi_results if r.sentiment == "positive")
    negative_volume = sum(1 for r in iedi_results if r.sentiment == "negative")
    neutral_volume = sum(1 for r in iedi_results if r.sentiment == "neutral")
    total_volume = len(iedi_results)
    
    # Calculate rates
    positivity_rate = (positive_volume / total_volume * 100) if total_volume > 0 else 0.0
    negativity_rate = (negative_volume / total_volume * 100) if total_volume > 0 else 0.0
    
    # Calculate IEDIs
    average_iedi = calculate_average_iedi(iedi_results)
    final_iedi = calculate_final_iedi(iedi_results, positive_volume, total_volume)
    
    return {
        "total_volume": total_volume,
        "positive_volume": positive_volume,
        "negative_volume": negative_volume,
        "neutral_volume": neutral_volume,
        "average_iedi": average_iedi,
        "final_iedi": final_iedi,
        "positivity_rate": round(positivity_rate, 2),
        "negativity_rate": round(negativity_rate, 2)
    }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example data
    banco_do_brasil = Bank(
        id=1,
        name="Banco do Brasil",
        variations=["BB", "Banco do Brasil S.A."]
    )
    
    relevant_outlets = [
        RelevantMediaOutlet(
            id=1,
            name="Valor Econômico",
            domain="valor.globo.com",
            category="Economia"
        )
    ]
    
    niche_outlets = [
        NicheMediaOutlet(
            id=1,
            name="Valor Econômico",
            domain="valor.globo.com",
            category="Economia",
            monthly_visitors=14_000_000
        )
    ]
    
    # Example mention (positive, full text available)
    mention_1 = {
        "sentiment": "positive",
        "title": "Banco do Brasil anuncia lucro recorde no trimestre",
        "snippet": "O Banco do Brasil divulgou ontem seus resultados...",
        "fullText": "O Banco do Brasil divulgou ontem seus resultados trimestrais, superando as expectativas do mercado. A instituição registrou lucro líquido de R$ 8,2 bilhões...",
        "domain": "valor.globo.com",
        "monthlyVisitors": 14_000_000
    }
    
    # Calculate IEDI
    result_1 = calculate_mention_iedi(
        mention_1,
        banco_do_brasil,
        relevant_outlets,
        niche_outlets
    )
    
    print("=== Mention 1 (Positive, Full Text) ===")
    print(f"IEDI Score: {result_1.score}/10")
    print(f"Sentiment: {result_1.sentiment}")
    print(f"Reach Group: {result_1.reach_group}")
    print(f"Numerator: {result_1.numerator}")
    print(f"Denominator: {result_1.denominator}")
    print(f"Subtitle Verified: {result_1.subtitle_verified}")
    print(f"Variables: {result_1.variables}")
    print()
    
    # Example mention (negative, paywall)
    mention_2 = {
        "sentiment": "negative",
        "title": "Bancos enfrentam críticas por tarifas abusivas",
        "snippet": "Bancos enfrentam críticas por tarifas abusivas",
        "fullText": "Bancos enfrentam críticas por tarifas abusivas",  # Same as snippet = paywall
        "domain": "folha.uol.com.br",
        "monthlyVisitors": 150_000_000
    }
    
    result_2 = calculate_mention_iedi(
        mention_2,
        banco_do_brasil,
        [RelevantMediaOutlet(2, "Folha de S.Paulo", "folha.uol.com.br", "Notícias")],
        []
    )
    
    print("=== Mention 2 (Negative, Paywall) ===")
    print(f"IEDI Score: {result_2.score}/10")
    print(f"Sentiment: {result_2.sentiment}")
    print(f"Reach Group: {result_2.reach_group}")
    print(f"Numerator: {result_2.numerator}")
    print(f"Denominator: {result_2.denominator}")
    print(f"Subtitle Verified: {result_2.subtitle_verified}")
    print(f"Variables: {result_2.variables}")
    print()
    
    # Aggregate results
    all_results = [result_1, result_2]
    aggregated = aggregate_bank_results(all_results)
    
    print("=== Aggregated Results ===")
    print(f"Total Volume: {aggregated['total_volume']}")
    print(f"Positive Volume: {aggregated['positive_volume']}")
    print(f"Negative Volume: {aggregated['negative_volume']}")
    print(f"Average IEDI: {aggregated['average_iedi']}/10")
    print(f"Final IEDI: {aggregated['final_iedi']}/10")
    print(f"Positivity Rate: {aggregated['positivity_rate']}%")
    print(f"Negativity Rate: {aggregated['negativity_rate']}%")
