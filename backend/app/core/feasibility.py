"""
Feasibility verification engine
Uses physics and engineering rules to validate product claims
"""
from typing import List, Dict, Optional, Tuple
from app.models.schemas import Claim, ClaimVerification


class FeasibilityEngine:
    """
    Rule-based engine to verify if product claims are technically feasible
    Uses physics, engineering constraints, and industry benchmarks
    """
    
    def __init__(self):
        # Define physical and engineering constraints by category
        self.constraints = {
            'battery_capacity': {
                'typical_range': (1000, 50000),  # mAh for portable devices
                'max_reasonable': 100000,  # mAh
                'density_limit': 250,  # Wh/kg (Li-ion theoretical max ~400)
                'common_sizes': [5000, 10000, 20000, 26800],  # Standard sizes
            },
            'charging_time': {
                'min_safe_time': 30,  # minutes for 10000mAh (more realistic)
                'typical_c_rating': 1,  # 1C charging is standard
                'fast_c_rating': 2,  # 2C is fast charging
                'theoretical_max_c': 3,  # 3C would be extreme and unsafe
            },
            'power_output': {
                'usb_standard': 5,  # Watts (5V 1A)
                'usb_fast': 18,  # Watts (9V 2A, QC 3.0)
                'usb_pd_standard': 45,  # Watts (USB-C PD typical)
                'usb_pd_max': 100,  # Watts (USB-C PD max)
                'portable_max': 65,  # Watts (reasonable for consumer portable)
                'realistic_max': 100,  # Watts (absolute max for portable)
            },
            'efficiency': {
                'typical_range': (75, 92),  # % for modern electronics
                'good_efficiency': 85,  # % considered good
                'theoretical_max': 95,  # % (very hard to exceed)
                'carnot_limit': 100,  # % (thermodynamic impossibility)
            },
            'speed': {
                'ebike_legal': 25,  # km/h (typical e-bike limit)
                'escooter_reasonable': 40,  # km/h
                'small_vehicle_max': 80,  # km/h
            },
            'range': {
                'powerbank_cycles': (300, 2000),  # charge cycles
                'ev_realistic': (100, 600),  # km for small EVs
            },
            'voltage': {
                'usb_standard': 5,  # Volts
                'usb_qc': [5, 9, 12],  # Quick Charge voltages
                'usb_pd': [5, 9, 12, 15, 20],  # PD voltages
                'max_safe': 20,  # Volts for consumer devices
            },
            'current': {
                'usb_standard': 1,  # Amps
                'usb_fast': 3,  # Amps (typical fast charge)
                'max_safe': 5,  # Amps for portable devices
            },
            'charge_cycles': {
                'minimum': 100,  # Very poor quality
                'typical_range': (300, 1000),  # Standard range
                'good_range': (500, 2000),  # Good quality
                'exceptional': 2000,  # Exceptional quality
                'impossible': 10000,  # Unrealistic claim
            },
            'warranty': {
                'typical_range': (3, 24),  # months
                'good_warranty': 24,  # 2 years
                'exceptional': 60,  # 5 years
                'suspicious': 120,  # 10+ years unlikely
            },
            'temperature': {
                'operating_range': (-20, 60),  # °C typical for electronics
                'extreme_low': -40,  # °C absolute minimum
                'extreme_high': 85,  # °C absolute maximum
            }
        }
        
        # Red flag keywords
        self.red_flag_keywords = [
            'quantum', 'miracle', 'magic', 'infinite', 'unlimited',
            '100% guaranteed', 'never fails', 'perpetual', 'eternal',
            'defies physics', 'breakthrough', 'revolutionary',
            'zero maintenance', 'maintenance-free', 'lasts forever',
            'impossible to break', 'indestructible', 'unbreakable'
        ]
    
    def verify_claims(self, claims: List[Claim]) -> List[ClaimVerification]:
        """
        Verify all claims and return verification results
        """
        verifications = []
        
        for claim in claims:
            verification = self._verify_single_claim(claim)
            verifications.append(verification)
        
        return verifications
    
    def _verify_single_claim(self, claim: Claim) -> ClaimVerification:
        """Verify a single claim based on its category"""
        
        # Route to appropriate verification method
        if claim.category == 'battery_capacity':
            return self._verify_battery_capacity(claim)
        elif claim.category == 'charging_time':
            return self._verify_charging_time(claim)
        elif claim.category == 'power_output':
            return self._verify_power_output(claim)
        elif claim.category == 'efficiency':
            return self._verify_efficiency(claim)
        elif claim.category == 'speed':
            return self._verify_speed(claim)
        elif claim.category == 'range':
            return self._verify_range(claim)
        elif claim.category == 'marketing_buzzword':
            return self._verify_buzzword(claim)
        elif claim.category == 'comparative':
            return self._verify_comparative(claim)
        elif claim.category == 'charge_cycles':
            return self._verify_charge_cycles(claim)
        elif claim.category == 'warranty':
            return self._verify_warranty(claim)
        elif claim.category == 'temperature':
            return self._verify_temperature(claim)
        elif claim.category == 'certifications':
            return self._verify_certifications(claim)
        elif claim.category == 'voltage':
            return self._verify_voltage(claim)
        elif claim.category == 'current':
            return self._verify_current(claim)
        else:
            return ClaimVerification(
                claim=claim.text,
                status='feasible',
                confidence=0.5,
                reasoning='Unable to verify - category not recognized',
                technical_details=None
            )
    
    def _verify_battery_capacity(self, claim: Claim) -> ClaimVerification:
        """Verify battery capacity claims"""
        value = claim.extracted_value
        if value is None:
            return self._create_verification(
                claim.text, 'feasible', 0.6,
                'Battery capacity mentioned but value not clearly specified'
            )
        
        constraints = self.constraints['battery_capacity']
        
        if value > constraints['max_reasonable']:
            return self._create_verification(
                claim.text, 'impossible', 0.95,
                f"Claimed {value}mAh is unrealistic for portable devices. "
                f"Even large power banks rarely exceed {constraints['max_reasonable']}mAh.",
                f"Would require extremely large/heavy battery. "
                f"Typical range: {constraints['typical_range'][0]}-{constraints['typical_range'][1]}mAh",
                flags=['impossible', 'unrealistic', 'high_capacity']
            )
        elif value > constraints['typical_range'][1]:
            return self._create_verification(
                claim.text, 'exaggerated', 0.85,
                f"{value}mAh is unusually high. Possible but would be very large and heavy.",
                f"Most portable power banks are {constraints['typical_range'][0]}-{constraints['typical_range'][1]}mAh",
                flags=['unusually_high', 'high_capacity']
            )
        elif value >= constraints['typical_range'][0]:
            return self._create_verification(
                claim.text, 'feasible', 0.9,
                f"{value}mAh is within normal range for portable power banks."
            )
        else:
            return self._create_verification(
                claim.text, 'feasible', 0.85,
                f"{value}mAh is low capacity but technically valid."
            )
    
    def _verify_charging_time(self, claim: Claim) -> ClaimVerification:
        """Verify charging time claims"""
        # Extract time in minutes
        text_lower = claim.text.lower()
        time_minutes = self._extract_time_in_minutes(text_lower, claim.extracted_value)
        
        if time_minutes is None:
            return self._create_verification(
                claim.text, 'feasible', 0.6,
                'Charging time mentioned but specifics unclear'
            )
        
        constraints = self.constraints['charging_time']
        
        if time_minutes < 5:
            return self._create_verification(
                claim.text, 'impossible', 0.95,
                f"Charging in {time_minutes} minutes is physically impossible for typical batteries. "
                "Even with highest charging rates, battery chemistry requires minimum time.",
                "Current technology limits: minimum ~15-30 minutes for fast charge of small batteries",
                flags=['impossible', 'unrealistic']
            )
        elif time_minutes < constraints['min_safe_time']:
            return self._create_verification(
                claim.text, 'exaggerated', 0.90,
                f"Charging in {time_minutes} minutes is extremely aggressive and likely unsafe. "
                "High risk of battery damage, overheating, or reduced lifespan.",
                f"Safe fast charging typically takes at least {constraints['min_safe_time']} minutes",
                flags=['unrealistic', 'unsafe']
            )
        elif time_minutes < 30:
            return self._create_verification(
                claim.text, 'feasible', 0.8,
                f"Fast charging in {time_minutes} minutes is possible with modern fast-charge technology, "
                "though may reduce battery lifespan over time."
            )
        else:
            return self._create_verification(
                claim.text, 'feasible', 0.95,
                f"Charging time of {time_minutes} minutes is reasonable and safe."
            )
    
    def _verify_power_output(self, claim: Claim) -> ClaimVerification:
        """Verify power output claims"""
        value = claim.extracted_value
        if value is None:
            return self._create_verification(
                claim.text, 'feasible', 0.6,
                'Power output mentioned but value not clear'
            )
        
        constraints = self.constraints['power_output']
        
        if value > constraints['portable_max']:
            return self._create_verification(
                claim.text, 'impossible', 0.90,
                f"{value}W output is unrealistic for portable devices. "
                f"USB-PD max is {constraints['usb_pd_max']}W. Higher power requires wall outlet.",
                "Portable devices are typically limited to 100W due to battery and safety constraints",
                flags=['impossible', 'unrealistic']
            )
        elif value > constraints['usb_pd_max']:
            return self._create_verification(
                claim.text, 'exaggerated', 0.85,
                f"{value}W exceeds USB Power Delivery standard ({constraints['usb_pd_max']}W max). "
                "Likely marketing exaggeration or requires special conditions.",
                flags=['unusually_high']
            )
        elif value > constraints['usb_fast']:
            return self._create_verification(
                claim.text, 'feasible', 0.90,
                f"{value}W is high power output but achievable with USB-PD technology."
            )
        else:
            return self._create_verification(
                claim.text, 'feasible', 0.95,
                f"{value}W is standard power output for modern USB devices."
            )
    
    def _verify_efficiency(self, claim: Claim) -> ClaimVerification:
        """Verify efficiency claims"""
        value = claim.extracted_value
        if value is None:
            return self._create_verification(
                claim.text, 'feasible', 0.6,
                'Efficiency mentioned but percentage not specified'
            )
        
        constraints = self.constraints['efficiency']
        
        if value >= 100:
            return self._create_verification(
                claim.text, 'impossible', 1.0,
                "100% or higher efficiency violates the laws of thermodynamics. "
                "All real devices lose some energy as heat.",
                "Second law of thermodynamics: no process can be 100% efficient",
                flags=['impossible', 'unrealistic', 'physics_violation']
            )
        elif value > constraints['theoretical_max']:
            return self._create_verification(
                claim.text, 'impossible', 0.95,
                f"{value}% efficiency is not achievable with current technology. "
                f"Even best-in-class devices rarely exceed {constraints['theoretical_max']}%.",
                "Best laboratory conditions achieve ~95-98% for power converters",
                flags=['impossible', 'unrealistic']
            )
        elif value > constraints['typical_range'][1]:
            return self._create_verification(
                claim.text, 'exaggerated', 0.85,
                f"{value}% efficiency is very high and unlikely for consumer products. "
                "Possible only in ideal laboratory conditions.",
                flags=['unusually_high']
            )
        elif value >= constraints['typical_range'][0]:
            return self._create_verification(
                claim.text, 'feasible', 0.90,
                f"{value}% efficiency is reasonable for modern electronic devices."
            )
        else:
            return self._create_verification(
                claim.text, 'feasible', 0.85,
                f"{value}% efficiency is low but technically possible for older or inefficient designs."
            )
    
    def _verify_speed(self, claim: Claim) -> ClaimVerification:
        """Verify speed claims for vehicles/devices"""
        value = claim.extracted_value
        if value is None:
            return self._create_verification(
                claim.text, 'feasible', 0.6,
                'Speed mentioned but value not clear'
            )
        
        constraints = self.constraints['speed']
        
        if value > constraints['small_vehicle_max']:
            return self._create_verification(
                claim.text, 'exaggerated', 0.80,
                f"{value} km/h is very high for small electric vehicles. "
                "May be dangerous and likely illegal for street use.",
                f"Typical e-bikes/scooters: {constraints['ebike_legal']}-{constraints['escooter_reasonable']} km/h"
            )
        elif value > constraints['escooter_reasonable']:
            return self._create_verification(
                claim.text, 'feasible', 0.75,
                f"{value} km/h is fast but achievable. Check local regulations - may be restricted."
            )
        else:
            return self._create_verification(
                claim.text, 'feasible', 0.90,
                f"{value} km/h is reasonable speed for personal electric vehicles."
            )
    
    def _verify_range(self, claim: Claim) -> ClaimVerification:
        """Verify range/distance claims"""
        value = claim.extracted_value
        if value is None:
            return self._create_verification(
                claim.text, 'feasible', 0.6,
                'Range mentioned but value not specified'
            )
        
        constraints = self.constraints['range']
        
        if value > constraints['ev_realistic'][1]:
            return self._create_verification(
                claim.text, 'exaggerated', 0.80,
                f"{value} km range is very high for small electric vehicles. "
                "Would require very large battery. Verify test conditions.",
                f"Typical small EV range: {constraints['ev_realistic'][0]}-{constraints['ev_realistic'][1]} km"
            )
        elif value >= constraints['ev_realistic'][0]:
            return self._create_verification(
                claim.text, 'feasible', 0.85,
                f"{value} km range is achievable for modern electric vehicles."
            )
        else:
            return self._create_verification(
                claim.text, 'feasible', 0.90,
                f"{value} km is conservative range estimate."
            )
    
    def _verify_buzzword(self, claim: Claim) -> ClaimVerification:
        """Verify marketing buzzwords"""
        text_lower = claim.text.lower()
        
        # Check for red flag keywords
        for red_flag in self.red_flag_keywords:
            if red_flag.lower() in text_lower:
                return self._create_verification(
                    claim.text, 'impossible', 0.90,
                    f"'{red_flag}' is a red flag term. Likely marketing hype with no scientific basis.",
                    "Be skeptical of extraordinary claims without evidence",
                    flags=['impossible', 'unrealistic', 'marketing_hype']
                )
        
        # Generic buzzwords
        if any(word in text_lower for word in ['ai-powered', 'ai powered']):
            return self._create_verification(
                claim.text, 'exaggerated', 0.75,
                "'AI-powered' is often marketing hype. True AI requires significant computational resources. "
                "May just be simple algorithms or microcontroller logic.",
                "Ask: What specific AI technology? What's the training data? What's the model?",
                flags=['marketing_hype']
            )
        
        if any(word in text_lower for word in ['medical-grade', 'medical grade']):
            return self._create_verification(
                claim.text, 'exaggerated', 0.80,
                "'Medical-grade' is loosely regulated term. Unless FDA/CE certified, it's likely marketing.",
                "True medical devices require regulatory approval and clinical testing"
            )
        
        if any(word in text_lower for word in ['military-grade', 'military grade']):
            return self._create_verification(
                claim.text, 'exaggerated', 0.75,
                "'Military-grade' has no standard definition for consumer products. "
                "Often just means 'durable' or 'rugged'.",
                "Military specifications (MIL-STD) are specific - ask which one"
            )
        
        return self._create_verification(
            claim.text, 'exaggerated', 0.70,
            "Marketing buzzword detected. Claims may be exaggerated or lack substance.",
            "Look for specific, measurable specifications instead of vague marketing terms"
        )
    
    def _verify_comparative(self, claim: Claim) -> ClaimVerification:
        """Verify comparative claims (2x faster, etc.)"""
        value = claim.extracted_value
        text_lower = claim.text.lower()
        
        if value and value > 10:
            return self._create_verification(
                claim.text, 'exaggerated', 0.85,
                f"{value}x better/faster is extremely high. Marketing exaggeration likely. "
                "Comparative claims without specific baseline are meaningless.",
                "Ask: Compared to what? Under what conditions? Measured how?"
            )
        elif 'best' in text_lower or 'fastest' in text_lower or 'most powerful' in text_lower:
            return self._create_verification(
                claim.text, 'exaggerated', 0.80,
                "Superlative claims ('best', 'fastest') are subjective and usually unprovable. "
                "Marketing hyperbole.",
                "Look for independent third-party testing and reviews"
            )
        elif value and value > 2:
            return self._create_verification(
                claim.text, 'exaggerated', 0.75,
                f"{value}x improvement is significant. May be true in specific scenarios but verify independently.",
                "Ask for details: compared to what specific product/standard?"
            )
        else:
            return self._create_verification(
                claim.text, 'feasible', 0.65,
                "Comparative claim made. Verify against independent benchmarks.",
                "Without baseline comparison, hard to validate"
            )
    
    def _extract_time_in_minutes(self, text: str, value: Optional[float]) -> Optional[float]:
        """Extract time duration in minutes"""
        if value is None:
            return None
        
        # Check if hours or minutes
        if 'hour' in text or 'hr' in text:
            return value * 60
        else:
            return value
    
    def _create_verification(
        self,
        claim: str,
        status: str,
        confidence: float,
        reasoning: str,
        technical_details: Optional[str] = None,
        flags: Optional[List[str]] = None
    ) -> ClaimVerification:
        """Helper to create verification object"""
        return ClaimVerification(
            claim=claim[:200],  # Truncate long claims
            status=status,
            confidence=confidence,
            reasoning=reasoning,
            technical_details=technical_details,
            flags=flags or []
        )
    
    def _verify_charge_cycles(self, claim: Claim) -> ClaimVerification:
        """Verify charge cycle claims"""
        value = claim.extracted_value
        if value is None:
            return self._create_verification(
                claim.text, 'feasible', 0.6,
                'Charge cycles mentioned but value not specified'
            )
        
        constraints = self.constraints['charge_cycles']
        
        if value > constraints['impossible']:
            return self._create_verification(
                claim.text, 'impossible', 0.95,
                f"{int(value)} cycles is unrealistic. Even premium batteries rarely exceed 2000-3000 cycles.",
                f"Typical Li-ion: {constraints['typical_range'][0]}-{constraints['typical_range'][1]} cycles",
                flags=['impossible', 'unrealistic']
            )
        elif value > constraints['exceptional']:
            return self._create_verification(
                claim.text, 'exaggerated', 0.80,
                f"{int(value)} cycles is exceptionally high. Possible for premium batteries but uncommon.",
                f"Good quality range: {constraints['good_range'][0]}-{constraints['good_range'][1]} cycles",
                flags=['unusually_high']
            )
        elif value >= constraints['good_range'][0]:
            return self._create_verification(
                claim.text, 'feasible', 0.90,
                f"{int(value)} cycles is good quality battery lifespan."
            )
        elif value >= constraints['typical_range'][0]:
            return self._create_verification(
                claim.text, 'feasible', 0.85,
                f"{int(value)} cycles is typical battery lifespan."
            )
        else:
            return self._create_verification(
                claim.text, 'feasible', 0.75,
                f"{int(value)} cycles is low quality but technically possible."
            )
    
    def _verify_warranty(self, claim: Claim) -> ClaimVerification:
        """Verify warranty claims"""
        value = claim.extracted_value
        if value is None:
            return self._create_verification(
                claim.text, 'feasible', 0.6,
                'Warranty mentioned but period not specified'
            )
        
        constraints = self.constraints['warranty']
        
        # Convert years to months if needed
        if 'year' in claim.text.lower() or 'yr' in claim.text.lower():
            value_months = value * 12
        else:
            value_months = value
        
        if value_months > constraints['suspicious']:
            return self._create_verification(
                claim.text, 'exaggerated', 0.80,
                f"{int(value_months/12)} year warranty is unusually long. Verify fine print for conditions.",
                f"Typical warranties: {constraints['typical_range'][0]}-{constraints['typical_range'][1]} months",
                flags=['unusually_high']
            )
        elif value_months >= constraints['good_warranty']:
            return self._create_verification(
                claim.text, 'feasible', 0.90,
                f"{int(value_months/12)} year warranty is good coverage."
            )
        elif value_months >= constraints['typical_range'][0]:
            return self._create_verification(
                claim.text, 'feasible', 0.85,
                f"{int(value_months)} month warranty is standard."
            )
        else:
            return self._create_verification(
                claim.text, 'feasible', 0.75,
                f"{int(value_months)} month warranty is minimal coverage."
            )
    
    def _verify_temperature(self, claim: Claim) -> ClaimVerification:
        """Verify operating temperature claims"""
        value = claim.extracted_value
        if value is None:
            return self._create_verification(
                claim.text, 'feasible', 0.6,
                'Temperature mentioned but range not specified'
            )
        
        constraints = self.constraints['temperature']
        
        if value < constraints['extreme_low'] or value > constraints['extreme_high']:
            return self._create_verification(
                claim.text, 'impossible', 0.90,
                f"Operating at {value}\u00b0C is unrealistic for consumer electronics.",
                f"Typical range: {constraints['operating_range'][0]} to {constraints['operating_range'][1]}\u00b0C",
                flags=['impossible', 'unrealistic']
            )
        elif value < constraints['operating_range'][0] or value > constraints['operating_range'][1]:
            return self._create_verification(
                claim.text, 'exaggerated', 0.75,
                f"{value}\u00b0C is extreme but possible with special design.",
                "Most consumer electronics operate in narrower range",
                flags=['extreme_conditions']
            )
        else:
            return self._create_verification(
                claim.text, 'feasible', 0.90,
                f"{value}\u00b0C is within normal operating range for electronics."
            )
    
    def _verify_certifications(self, claim: Claim) -> ClaimVerification:
        """Verify certification claims"""
        text_lower = claim.text.lower()
        
        # Major legitimate certifications
        legitimate_certs = ['ce', 'fcc', 'rohs', 'ul', 'etl', 'csa', 'mfi', 'iso']
        has_legit = any(cert in text_lower for cert in legitimate_certs)
        
        if has_legit:
            return self._create_verification(
                claim.text, 'feasible', 0.85,
                "Legitimate certifications mentioned. Verify on manufacturer website.",
                "Check for certification numbers and regulatory body verification"
            )
        else:
            return self._create_verification(
                claim.text, 'exaggerated', 0.70,
                "Certification claimed but unclear if legitimate. Verify independently.",
                "Look for specific certification numbers and issuing body"
            )
    
    def _verify_voltage(self, claim: Claim) -> ClaimVerification:
        """Verify voltage claims"""
        value = claim.extracted_value
        if value is None:
            return self._create_verification(
                claim.text, 'feasible', 0.6,
                'Voltage mentioned but value not specified'
            )
        
        constraints = self.constraints['voltage']
        
        if value > constraints['max_safe']:
            return self._create_verification(
                claim.text, 'impossible', 0.90,
                f"{value}V exceeds safe limits for consumer portable devices.",
                f"USB-PD max: {constraints['max_safe']}V. Higher voltages require special handling.",
                flags=['impossible', 'unrealistic', 'safety_concern']
            )
        elif value in constraints['usb_pd']:
            return self._create_verification(
                claim.text, 'feasible', 0.95,
                f"{value}V is standard USB Power Delivery voltage."
            )
        elif value == constraints['usb_standard']:
            return self._create_verification(
                claim.text, 'feasible', 0.95,
                f"{value}V is standard USB voltage."
            )
        else:
            return self._create_verification(
                claim.text, 'feasible', 0.75,
                f"{value}V is non-standard but technically possible. Verify compatibility."
            )
    
    def _verify_current(self, claim: Claim) -> ClaimVerification:
        """Verify current/amperage claims"""
        value = claim.extracted_value
        if value is None:
            return self._create_verification(
                claim.text, 'feasible', 0.6,
                'Current mentioned but value not specified'
            )
        
        constraints = self.constraints['current']
        
        if value > constraints['max_safe']:
            return self._create_verification(
                claim.text, 'impossible', 0.85,
                f"{value}A exceeds safe limits for portable USB devices.",
                f"Typical USB fast charge: {constraints['usb_fast']}A max. Higher requires specialized cables.",
                flags=['impossible', 'unrealistic', 'safety_concern']
            )
        elif value >= constraints['usb_fast']:
            return self._create_verification(
                claim.text, 'feasible', 0.90,
                f"{value}A is fast charging current. Requires proper cables and port."
            )
        elif value >= constraints['usb_standard']:
            return self._create_verification(
                claim.text, 'feasible', 0.95,
                f"{value}A is standard to moderate charging current."
            )
        else:
            return self._create_verification(
                claim.text, 'feasible', 0.85,
                f"{value}A is low current, slower charging."
            )

