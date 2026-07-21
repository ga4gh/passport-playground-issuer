"""Prototype port of DUOS's PassportService.generateDataPassport, backed by a static JSON file
instead of a database. See PassportResource/PassportService in the Consent (DUOS) repo for the
original Java implementation.
"""
import json
import time
from datetime import datetime
from pathlib import Path

ISS = "https://duos.org"
EXPIRATION_SECONDS = 3600
IDENTIFIER_PREFIX = "DUOS-"

DATA_FILE = Path(__file__).parent / "data" / "passport_data.json"


class NotFoundError(Exception):
    pass


class BadRequestError(Exception):
    pass


def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)


def format_identifier(alias):
    return f"{IDENTIFIER_PREFIX}{alias:06d}"


def parse_identifier_to_alias(dataset_identifier):
    if not dataset_identifier.startswith(IDENTIFIER_PREFIX):
        raise BadRequestError(f"Invalid dataset identifier: {dataset_identifier}")
    try:
        return int(dataset_identifier[len(IDENTIFIER_PREFIX):])
    except ValueError:
        raise BadRequestError(f"Invalid dataset identifier: {dataset_identifier}")


def find_dataset_by_alias(data, alias):
    return next((d for d in data["datasets"] if d["alias"] == alias), None)


def find_dac_by_id(data, dac_id):
    return next((d for d in data["dacs"] if d["dacId"] == dac_id), None)


def find_daa_by_id(data, daa_id):
    return next((d for d in data["daas"] if d["daaId"] == daa_id), None)


def data_use_to_term_array(data_use):
    terms = []
    if not data_use:
        return terms
    if data_use.get("generalUse"):
        terms.append("DUO:0000004")
    if data_use.get("hmbResearch"):
        terms.append("DUO:0000006")
    disease_restrictions = data_use.get("diseaseRestrictions") or []
    if disease_restrictions:
        terms.append("DUO:0000007")
        terms.extend(disease_restrictions)
    if data_use.get("populationOriginsAncestry"):
        terms.append("DUO:0000011")
    if data_use.get("geneticStudiesOnly"):
        terms.append("DUO:0000016")
    if data_use.get("methodsResearch"):
        terms.append("DUO:0000015")
    if data_use.get("nonProfitUse"):
        terms.append("DUO:0000018")
    if data_use.get("publicationResults"):
        terms.append("DUO:0000019")
    if data_use.get("collaboratorRequired"):
        terms.append("DUO:0000020")
    if data_use.get("ethicsApprovalRequired"):
        terms.append("DUO:0000021")
    if data_use.get("geographicalRestrictions"):
        terms.append("DUO:0000022")
    if data_use.get("publicationMoratorium"):
        terms.append("DUO:0000024")
    return terms


def epoch_seconds_from_create_date(create_date, default=None):
    if not create_date:
        return default if default is not None else int(time.time())
    return int(datetime.fromisoformat(create_date.replace("Z", "+00:00")).timestamp())


def get_approved_users_endpoint(dataset_identifier):
    return (
        "https://consent.dsde-prod.broadinstitute.org/api/datataset/"
        f"{dataset_identifier}/approvedUsers"
    )


def visa_from_claim(dataset_identifier, claim_type, asserted, value, by):
    now = int(time.time())
    return {
        "iss": ISS,
        "sub": dataset_identifier,
        "iat": now,
        "exp": now + EXPIRATION_SECONDS,
        "ga4gh_visa_v1": {
            "type": claim_type,
            "asserted": asserted,
            "value": value,
            "source": ISS,
            "by": by,
        },
    }


def generate_data_passport(dataset_identifier):
    alias = parse_identifier_to_alias(dataset_identifier)
    data = load_data()
    dataset = find_dataset_by_alias(data, alias)
    if dataset is None:
        raise NotFoundError(f"Dataset not found: {dataset_identifier}")

    now = int(time.time())
    visas = []

    # ApprovedUsers - links to the API endpoint describing approved users for the dataset
    visas.append(
        visa_from_claim(
            dataset_identifier,
            "ApprovedUsers",
            now,
            get_approved_users_endpoint(dataset_identifier),
            "dac",
        )
    )

    # ConsentedDataUseTerms - always present if the dataset exists
    visas.append(
        visa_from_claim(
            dataset_identifier,
            "ConsentedDataUseTerms",
            epoch_seconds_from_create_date(dataset.get("createDate")),
            data_use_to_term_array(dataset.get("dataUse")),
            "dac",
        )
    )

    # OversightBodies + RequiredAgreements - only when the dataset is associated with a DAC
    dac_id = dataset.get("dacId")
    if dac_id is not None:
        dac = find_dac_by_id(data, dac_id)
        if dac is not None:
            visas.append(
                visa_from_claim(
                    dataset_identifier,
                    "OversightBodies",
                    epoch_seconds_from_create_date(dac.get("createDate")),
                    f"{ISS}/dac/{dac['dacId']}",
                    "dac",
                )
            )
            daa_id = dac.get("associatedDaaId")
            if daa_id is not None:
                daa = find_daa_by_id(data, daa_id)
                if daa is not None:
                    visas.append(
                        visa_from_claim(
                            dataset_identifier,
                            "RequiredAgreements",
                            epoch_seconds_from_create_date(daa.get("createDate")),
                            f"{ISS}/daa/{daa['daaId']}",
                            "so",
                        )
                    )

    return {"ga4gh_passport_v1": visas}
