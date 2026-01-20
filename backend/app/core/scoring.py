"""
Scoring engine - generates final scores and verdicts
"""
from typing import List, Tuple
from app.models.schemas import (
    ClaimVerification, PriceAnalysis, ProductAnalysis,
    Claim, ProductData
)


class ScoringEngine:
    """
    Generates reality score, pricing score, and overall verdict
    """
    
    def generate_analysis(
        self,
        product_data: ProductData,
        claims: List[Claim],
        verifications: List[ClaimVerification],
        price_analysis: PriceAnalysis | None
    ) -> ProductAnalysis:
        """Generate complete product analysis with scores and verdict"""
        
        # Calculate reality score (0-100)
        reality_score = self._calculate_reality_score(verifications)
        
        # Calculate pricing score (0-100)
        pricing_score = self._calculate_pricing_score(price_analysis)
        
        # Determine overall verdict
        overall_verdict = self._determine_overall_verdict(
            reality_score, pricing_score, verifications
        )
        
        # Generate summary
        summary = self._generate_summary(
            reality_score, pricing_score, overall_verdict, verifications
        )
        
        # Extract red flags
        red_flags = self._extract_red_flags(verifications, price_analysis)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            reality_score, pricing_score, verifications, price_analysis
        )
        
        return ProductAnalysis(
            product_title=product_data.title,
            claims_found=claims,
            verifications=verifications,
            price_analysis=price_analysis,
            reality_score=round(reality_score, 1),
            pricing_score=round(pricing_score, 1),
            overall_verdict=overall_verdict,
            summary=summary,
            red_flags=red_flags,
            recommendations=recommendations
        )
    
    def _calculate_reality_score(
        self, verifications: List[ClaimVerification]
    ) -> float:
        """
        Calculate reality score based on claim verifications
        100 = all claims feasible and realistic
        0 = all claims impossible or highly exaggerated
        """
        if not verifications:
            return 75.0  # Neutral-positive score if no specific claims to verify
        
        total_score = 0.0
        total_weight = 0.0
        
        # Count critical flags
        critical_flags = sum(1 for v in verifications if 'impossible' in v.flags or 'unrealistic' in v.flags)
        
        for verification in verifications:
            # Higher weight for higher confidence
            weight = verification.confidence
            
            # Score by status with nuance
            if verification.status == 'feasible':
                if any(flag in verification.flags for flag in ['high_capacity', 'unusually_high']):
                    score = 85.0  # Good but not perfect for edge cases
                else:
                    score = 100.0  # Perfect for normal feasible claims
            elif verification.status == 'exaggerated':
                score = 40.0  # Penalty for exaggeration
            else:  # impossible
                score = 0.0  # Zero for impossible claims
            
            total_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 75.0
        
        base_score = total_score / total_weight
        
        # Apply penalty for multiple critical issues
        if critical_flags >= 3:
            base_score *= 0.5  # 50% penalty for many impossible claims
        elif critical_flags >= 2:
            base_score *= 0.7  # 30% penalty
        
        return max(0.0, min(100.0, base_score))
    
    def _calculate_pricing_score(
        self, price_analysis: PriceAnalysis | None
    ) -> float:
        """
        Calculate pricing fairness score
        100 = excellent value (underpriced)
        50 = fair market price
        0 = extremely overpriced or suspiciously cheap
        """
        if price_analysis is None:
            return 50.0  # Neutral if no price data
        
        # More nuanced scoring with suspiciously_cheap detection
        verdict_scores = {
            'suspiciously_cheap': 20.0,  # Possible counterfeit
            'excellent_value': 100.0,
            'good_value': 90.0,
            'fair': 75.0,
            'slightly_overpriced': 55.0,
            'overpriced': 30.0,
            'highly_overpriced': 10.0
        }
        
        base_score = verdict_scores.get(price_analysis.verdict, 50.0)
        
        # Adjust based on overpricing percentage
        if price_analysis.overpricing_percentage:
            if price_analysis.overpricing_percentage < -30:  # Extremely cheap
                # Could be too good to be true
                base_score = min(85, base_score - 10)
            elif price_analysis.overpricing_percentage < -10:  # Good deal
                base_score = min(100, base_score + 5)
            elif price_analysis.overpricing_percentage > 150:  # More than 2.5x fair price
                base_score = max(0, base_score - 30)
            elif price_analysis.overpricing_percentage > 100:  # Double the fair price
                base_score = max(0, base_score - 20)
        
        return base_score
    
    def _determine_overall_verdict(
        self,
        reality_score: float,
        pricing_score: float,
        verifications: List[ClaimVerification]
    ) -> str:
        """Determine overall product verdict"""
        
        # Check for impossible claims
        impossible_count = sum(
            1 for v in verifications if v.status == 'impossible'
        )
        
        if impossible_count > 0:
            return 'not_recommended'
        
        # Check for many exaggerated claims
        exaggerated_count = sum(
            1 for v in verifications if v.status == 'exaggerated'
        )
        
        if exaggerated_count > len(verifications) * 0.5:  # >50% exaggerated
            return 'misleading_claims'
        
        # Combined score evaluation with weighted factors
        combined_score = (reality_score * 0.65 + pricing_score * 0.35)  # Reality matters more
        
        # Stricter verdicts based on combined analysis
        if combined_score >= 85 and reality_score >= 75 and pricing_score >= 70:
            return 'excellent_choice'
        elif combined_score >= 75 and reality_score >= 65:
            return 'good_value'
        elif pricing_score < 40:
            return 'overpriced'
        elif reality_score < 50:
            return 'misleading_claims'
        elif combined_score >= 60:
            return 'acceptable'
        else:
            return 'not_recommended'
    
    def _generate_summary(
        self,
        reality_score: float,
        pricing_score: float,
        verdict: str,
        verifications: List[ClaimVerification]
    ) -> str:
        """Generate user-friendly summary"""
        
        verdict_messages = {
            'excellent_choice': "Excellent product with realistic claims and great value. Highly recommended.",
            'good_value': "Good product with realistic claims and fair pricing. Recommended.",
            'acceptable': "Acceptable product with some valid points but also concerns worth noting.",
            'overpriced': "Product is significantly overpriced compared to market value.",
            'misleading_claims': "Product makes several misleading or exaggerated claims. Proceed with caution.",
            'not_recommended': "Product makes technically impossible claims or has major red flags. Not recommended."
        }
        
        base_message = verdict_messages.get(
            verdict,
            "Product has mixed characteristics requiring careful consideration."
        )
        
        # Add detail about scores
        if reality_score < 50:
            base_message += " Many claims appear exaggerated or physically impossible."
        elif reality_score < 70:
            base_message += " Some claims appear questionable or exaggerated."
        elif reality_score >= 85:
            base_message += " Product claims are largely credible."
        
        if pricing_score < 50:
            base_message += " Pricing is higher than justified by features."
        elif pricing_score >= 85:
            base_message += " Pricing is fair or better than average."
        
        return base_message
    
    def _extract_red_flags(
        self,
        verifications: List[ClaimVerification],
        price_analysis: PriceAnalysis | None
    ) -> List[str]:
        """Extract red flags for user attention"""
        red_flags = []
        
        # Check for impossible claims with details
        impossible_claims = [v for v in verifications if v.status == 'impossible']
        for verification in impossible_claims[:3]:  # Limit to top 3
            red_flags.append(
                f"❌ Impossible claim: {verification.claim[:80]}... ({verification.reasoning[:60]})"
            )
        
        if len(impossible_claims) > 3:
            red_flags.append(f"❌ Plus {len(impossible_claims) - 3} more impossible claims")
        
        # Check for exaggerated claims
        exaggerated = [v for v in verifications if v.status == 'exaggerated']
        if len(exaggerated) >= 4:
            red_flags.append(
                f"⚠️ Multiple exaggerated claims detected ({len(exaggerated)} found) - marketing hype likely"
            )
        elif len(exaggerated) >= 2:
            red_flags.append(
                f"⚠️ Some claims appear exaggerated ({len(exaggerated)} found)"
            )
        
        # Price red flags with more context
        if price_analysis:
            if price_analysis.verdict == 'suspiciously_cheap':
                red_flags.append(
                    "🚨 Price is suspiciously low - possible counterfeit or quality issues"
                )
            elif price_analysis.overpricing_percentage > 100:
                red_flags.append(
                    f"💰 Severely overpriced ({price_analysis.overpricing_percentage:.0f}% above fair value)"
                )
            elif price_analysis.overpricing_percentage > 50:
                red_flags.append(
                    f"💰 Overpriced by {price_analysis.overpricing_percentage:.0f}% compared to similar products"
                )
        
        # Safety concerns from flags
        safety_issues = [v for v in verifications if 'safety_concern' in v.flags]
        if safety_issues:
            red_flags.append(
                "⚡ Safety concerns detected - verify certifications and user reviews"
            )
        
        # Buzzword overuse
        buzzwords = [v for v in verifications if v.category == 'marketing_buzzword']
        if len(buzzwords) > 3:
            red_flags.append(
                "📢 Heavy use of marketing buzzwords without substantiation"
            )
        
        if not red_flags:
            red_flags.append("✅ No major red flags detected")
        
        return red_flags
    
    def _generate_recommendations(
        self,
        reality_score: float,
        pricing_score: float,
        verifications: List[ClaimVerification],
        price_analysis: PriceAnalysis | None
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Reality-based recommendations
        if reality_score < 50:
            recommendations.append(
                "🚫 Strongly recommend avoiding - claims are unrealistic or impossible"
            )
            recommendations.append(
                "🔍 Check consumer protection reviews and complaint databases"
            )
        elif reality_score < 70:
            recommendations.append(
                "⚠️ Research thoroughly - verify all claims with independent sources"
            )
            recommendations.append(
                "📧 Contact seller for detailed specifications and proof of claims"
            )
        
        # Pricing recommendations
        if price_analysis:
            if price_analysis.verdict == 'suspiciously_cheap':
                recommendations.append(
                    "🔎 Verify authenticity - price may indicate counterfeit product"
                )
                recommendations.append(
                    "🛡️ Buy from authorized sellers only to ensure genuine product"
                )
            elif pricing_score < 40:
                recommendations.append(
                    f"💵 Overpriced - fair value is ${price_analysis.fair_price_min:.0f}-"
                    f"${price_analysis.fair_price_max:.0f}. Consider alternatives"
                )
                recommendations.append(
                    "🛍️ Wait for sales or compare with similar products from other brands"
                )
            elif pricing_score > 85:
                recommendations.append(
                    "👍 Price is fair or better - good value if claims are verified"
                )
        
        # Specific claim recommendations
        impossible = [v for v in verifications if v.status == 'impossible']
        if impossible:
            recommendations.append(
                f"❌ Avoid products with {len(impossible)} impossible claim(s) - indicates dishonest marketing"
            )
        
        # Certification recommendations
        cert_claims = [v for v in verifications if v.category == 'certifications']
        if cert_claims:
            recommendations.append(
                "🏅 Verify certifications on official regulatory websites (FCC, CE, etc.)"
            )
        
        # Warranty recommendations
        warranty_claims = [v for v in verifications if v.category == 'warranty']
        if warranty_claims:
            recommendations.append(
                "📄 Read warranty terms carefully - check coverage limits and claim process"
            )
        
        # General recommendation if product looks good
        if reality_score >= 80 and pricing_score >= 70:
            recommendations.append(
                "✅ Product appears genuine with realistic specs - recommended if it fits your needs"
            )
            recommendations.append(
                "📱 Still check recent user reviews for real-world performance feedback"
            )
        
        if not recommendations:
            recommendations.append(
                "📊 Product is acceptable but do basic research before purchasing"
            )
        
        return recommendations
        if impossible:
            recommendations.append(
                "🚫 Avoid this product - impossible claims indicate unreliable seller"
            )
        
        # General recommendations
        if reality_score >= 75 and pricing_score >= 70:
            recommendations.append(
                "✨ This product appears legitimate - read user reviews to confirm"
            )
        else:
            recommendations.append(
                "🔎 Research competitor products before making decision"
            )
        
        return recommendations
